
import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [numSlides, setNumSlides] = useState(5);
  const [aesthetic, setAesthetic] = useState('Cinematic');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [inputMode, setInputMode] = useState('topic'); // 'topic' or 'paste'
  const [pastedText, setPastedText] = useState('');

  const [selectedImage, setSelectedImage] = useState(null);
  const [generatedSlides, setGeneratedSlides] = useState([]); // Store slide data
  const [storyCaption, setStoryCaption] = useState(''); // Overall caption for the story
  const [storyHashtags, setStoryHashtags] = useState([]); // Overall hashtags
  const [completedResearch, setCompletedResearch] = useState(null); // Store research after generation
  const [researchCollapsed, setResearchCollapsed] = useState(true); // Research panel collapsed state
  const [generatingPhase, setGeneratingPhase] = useState(null); // 'research' or 'images'
  const [expectedSlides, setExpectedSlides] = useState(0); // Number of slides being generated
  const [currentGeneratingSlide, setCurrentGeneratingSlide] = useState(0); // Which slide is being generated (1-indexed)
  const [generatingSlides, setGeneratingSlides] = useState([]); // Slides being generated (for display)

  // Trending topics
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [suggestedTopics, setSuggestedTopics] = useState([]);
  const [loadingTopics, setLoadingTopics] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);
  const [topicsError, setTopicsError] = useState(null);

  const categories = [
    { id: 'tech', label: 'Tech', icon: '💻' },
    { id: 'ai', label: 'AI', icon: '🤖' },
    { id: 'india', label: 'India', icon: '🇮🇳' },
    { id: 'world', label: 'World', icon: '🌍' },
    { id: 'politics', label: 'Politics', icon: '🏛️' },
    { id: 'sports', label: 'Sports', icon: '⚽' },
    { id: 'movies', label: 'Movies', icon: '🎬' },
    { id: 'business', label: 'Business', icon: '💼' },
    { id: 'finance', label: 'Finance', icon: '📈' },
    { id: 'science', label: 'Science', icon: '🔬' },
  ];

  const handleCategorySelect = (categoryId) => {
    let newCategories;
    if (selectedCategories.includes(categoryId)) {
      newCategories = selectedCategories.filter(c => c !== categoryId);
    } else {
      if (selectedCategories.length >= 3) return; // Max 3 limit
      newCategories = [...selectedCategories, categoryId];
    }

    setSelectedCategories(newCategories);

    if (newCategories.length === 0) {
      setSelectedSuggestion(null);
      setSuggestedTopics([]);
      setLoadingTopics(false);
      setTopicsError(null);
      return;
    }

    // Immediate feedback: Set a default generic topic
    const getLabel = (id) => categories.find(c => c.id === id)?.label || id;
    const labels = newCategories.map(getLabel);
    const defaultTopic = `Trending ${labels.join(' & ')} News`;
    setSelectedSuggestion(defaultTopic);

    // Stop: Do NOT auto fetch. User must click a button if they want specific headlines.
    setSuggestedTopics([]);
    setLoadingTopics(false);
    setTopicsError(null);
  };

  const handleFetchTopics = async () => {
    if (selectedCategories.length === 0) return;

    setLoadingTopics(true);
    setSuggestedTopics([]);
    setTopicsError(null);

    try {
      const response = await fetch(`http://localhost:8000/trending_topics?categories=${selectedCategories.join(',')}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestedTopics(data.topics || []);
        setLoadingTopics(false);
      } else {
        setTopicsError('Failed to load topics');
        setLoadingTopics(false);
      }
    } catch (err) {
      console.error('Failed to fetch topics:', err);
      setTopicsError('Network error');
      setLoadingTopics(false);
    }
  };

  const handleTopicSuggestionClick = (e, suggestedTopic) => {
    e.preventDefault();
    e.stopPropagation();
    e.nativeEvent.stopImmediatePropagation();
    console.log('Topic clicked:', suggestedTopic);
    setSelectedSuggestion(suggestedTopic);
  };

  const handleApplySuggestion = (e) => {
    e.preventDefault();
    e.stopPropagation();

    // Logic: If the suggestion is the generic "Trending X News", then fetch specific headlines.
    // Otherwise, apply it to the input field, but KEEP the categories/suggestions open so user can change their mind.

    if (selectedSuggestion && selectedSuggestion.startsWith('Trending ') && selectedSuggestion.endsWith(' News')) {
      handleFetchTopics();
      return;
    }

    if (selectedSuggestion) {
      setTopic(selectedSuggestion);
      // Removed: setSuggestedTopics([]); 
      // Removed: setSelectedCategories([]);
      setSelectedSuggestion(null); // Just deselect the item, but keep list visible
      setLoadingTopics(false);
      setTopicsError(null);
    }
  };

  // Pinterest-style boards
  const [activeTab, setActiveTab] = useState('research'); // 'research' or 'images'
  const [savedResearch, setSavedResearch] = useState([]); // Array of saved research boards
  const [savedImageBoards, setSavedImageBoards] = useState([]); // Array of saved image boards
  const [selectedBoard, setSelectedBoard] = useState(null); // Currently selected image board for viewing
  const [selectedResearchBoard, setSelectedResearchBoard] = useState(null); // Currently selected research board for viewing

  // Dummy fallback for better UX demo if API fails
  const aesthetics = [
    'Cinematic', 'Vintage', 'Cyberpunk', 'Minimalist',
    'Watercolor', 'Playful', 'Dark Fantasy', 'Abstract',
    'Comic Book', 'Manga'
  ];

  const [storyPlan, setStoryPlan] = useState(null); // New state for holding the research plan

  // Cycle through slides during generation (approximate timing)
  useEffect(() => {
    if (generatingPhase === 'images' && currentGeneratingSlide < expectedSlides) {
      const timer = setTimeout(() => {
        setCurrentGeneratingSlide(prev => Math.min(prev + 1, expectedSlides));
      }, 12000); // ~12 seconds per slide (Gemini image generation is slow)
      return () => clearTimeout(timer);
    }
  }, [generatingPhase, currentGeneratingSlide, expectedSlides]);

  const handleGenerate = async (e) => {
    e.preventDefault();

    // Validate based on mode
    if (inputMode === 'topic' && !topic) return;
    if (inputMode === 'paste' && !pastedText.trim()) return;

    setIsGenerating(true);
    setGeneratingPhase('research');
    setGeneratedImages([]);
    setGeneratedSlides([]);
    setStoryCaption('');
    setStoryHashtags([]);
    setStoryPlan(null);
    setCompletedResearch(null);
    setResearchCollapsed(true);

    try {
      let response;

      if (inputMode === 'paste') {
        // Generate slides from pasted text
        response = await fetch('http://localhost:8000/plan_from_text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: pastedText,
            num_slides: numSlides,
            aesthetic,
            topic: topic || 'Custom Content'
          }),
        });
      } else {
        // Research topic mode
        response = await fetch('http://localhost:8000/plan_story', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic, num_slides: numSlides, aesthetic }),
        });
      }

      if (!response.ok) throw new Error('Planning failed');

      const data = await response.json();
      setStoryPlan(data.plan); // Store plan for user review

    } catch (err) {
      console.error(err);
      alert("Failed to plan story. Check backend.");
    } finally {
      setIsGenerating(false);
      setGeneratingPhase(null);
    }
  };

  const handleConfirmPlan = async () => {
    if (!storyPlan) return;
    setIsGenerating(true);
    setGeneratingPhase('images');
    setExpectedSlides(storyPlan.slides?.length || 0);
    setGeneratingSlides(storyPlan.slides || []);
    setCurrentGeneratingSlide(1);

    try {
      // Step 2: Confirm and Generate Images
      const response = await fetch('http://localhost:8000/generate_from_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: storyPlan }),
      });

      if (!response.ok) throw new Error('Generation failed');

      const data = await response.json();
      setGeneratedImages(data.images);
      setGeneratedSlides(storyPlan.slides);
      setStoryCaption(storyPlan.caption || '');
      setStoryHashtags(storyPlan.hashtags || []);
      setCompletedResearch(storyPlan);
      setResearchCollapsed(true);

      // Save to boards
      const newResearchBoard = {
        id: Date.now(),
        topic: storyPlan.topic,
        aesthetic: storyPlan.aesthetic,
        slides: storyPlan.slides,
        sources: storyPlan.sources,
        caption: storyPlan.caption,
        hashtags: storyPlan.hashtags,
        createdAt: new Date().toISOString()
      };
      const newImageBoard = {
        id: Date.now(),
        topic: storyPlan.topic,
        images: data.images,
        slides: storyPlan.slides,
        caption: storyPlan.caption,
        hashtags: storyPlan.hashtags,
        aesthetic: aesthetic,
        createdAt: new Date().toISOString()
      };
      setSavedResearch(prev => [newResearchBoard, ...prev]);
      setSavedImageBoards(prev => [newImageBoard, ...prev]);
      setSelectedBoard(newImageBoard);
      setActiveTab('images');

      setStoryPlan(null); // Clear active plan

    } catch (err) {
      console.error(err);
      alert("Failed to generate final story.");
    } finally {
      setIsGenerating(false);
      setGeneratingPhase(null);
    }
  };

  const handleEditAesthetic = (field, value) => {
    if (!storyPlan) return;
    setStoryPlan({
      ...storyPlan,
      aesthetic: {
        ...storyPlan.aesthetic,
        [field]: value
      }
    });
  };

  const handleEditSlide = (slideIndex, field, value) => {
    if (!storyPlan) return;
    const updatedSlides = [...storyPlan.slides];
    updatedSlides[slideIndex] = {
      ...updatedSlides[slideIndex],
      [field]: value
    };
    setStoryPlan({
      ...storyPlan,
      slides: updatedSlides
    });
  };

  const handleEditCaption = (value) => {
    if (!storyPlan) return;
    setStoryPlan({
      ...storyPlan,
      caption: value
    });
  };

  // Edit completed research
  const handleEditCompletedResearch = (field, value, slideIndex = null) => {
    if (!completedResearch) return;
    if (slideIndex !== null) {
      const updatedSlides = [...completedResearch.slides];
      updatedSlides[slideIndex] = { ...updatedSlides[slideIndex], [field]: value };
      setCompletedResearch({ ...completedResearch, slides: updatedSlides });
    } else {
      setCompletedResearch({ ...completedResearch, [field]: value });
    }
  };

  // Regenerate images from research (can pass research directly or use completedResearch)
  const handleRegenerateImages = async (researchToUse = null) => {
    const research = researchToUse || completedResearch;
    if (!research) return;

    setCompletedResearch(research);
    setSelectedResearchBoard(null);
    setIsGenerating(true);
    setGeneratingPhase('images');
    setExpectedSlides(research.slides?.length || 0);
    setResearchCollapsed(true);

    try {
      const response = await fetch('http://localhost:8000/generate_from_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: research }),
      });

      if (!response.ok) throw new Error('Regeneration failed');

      const data = await response.json();
      setGeneratedImages(data.images);
      setGeneratedSlides(research.slides);
      setStoryCaption(research.caption || '');
      setStoryHashtags(research.hashtags || []);

      // Update the saved board with new images
      const newImageBoard = {
        id: Date.now(),
        topic: research.topic,
        images: data.images,
        slides: research.slides,
        caption: research.caption,
        hashtags: research.hashtags,
        aesthetic: research.aesthetic?.art_style,
        createdAt: new Date().toISOString()
      };
      setSavedImageBoards(prev => [newImageBoard, ...prev]);
      setSelectedBoard(newImageBoard);
      setActiveTab('images');

    } catch (err) {
      console.error(err);
      alert("Failed to regenerate images.");
    } finally {
      setIsGenerating(false);
      setGeneratingPhase(null);
    }
  };

  // Download image
  const handleDownloadImage = async (imageUrl, index) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `slide_${index + 1}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  // Download all images
  const handleDownloadAll = async (images) => {
    for (let i = 0; i < images.length; i++) {
      await handleDownloadImage(images[i], i);
      await new Promise(r => setTimeout(r, 300)); // Small delay between downloads
    }
  };


  return (
    <div className="app-container">
      {/* Sidebar - Controls */}
      <aside className="sidebar">
        <div className="control-panel">
          <div className="panel-header">
            <span className="panel-eyebrow">AI-Powered</span>
            <h2 className="panel-title">Create Visual Stories</h2>
            <p className="panel-subtitle">Transform any idea into stunning social media narratives with AI research and generation.</p>
          </div>

          <form onSubmit={handleGenerate}>
            {/* Mode Toggle */}
            <div className="mode-toggle">
              <button
                type="button"
                className={`mode-btn ${inputMode === 'topic' ? 'active' : ''}`}
                onClick={() => setInputMode('topic')}
                disabled={isGenerating || storyPlan !== null}
              >
                Research Topic
              </button>
              <button
                type="button"
                className={`mode-btn ${inputMode === 'paste' ? 'active' : ''}`}
                onClick={() => setInputMode('paste')}
                disabled={isGenerating || storyPlan !== null}
              >
                Paste Text
              </button>
            </div>

            {inputMode === 'topic' ? (
              /* Topic Input */
              <div className="input-group">
                <label className="input-label">Story Topic</label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    className="topic-input"
                    placeholder="e.g. Ancient temples of Angkor Wat..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    disabled={isGenerating || storyPlan !== null}
                  />
                </div>

                {/* Category Chips */}
                {!isGenerating && !storyPlan && (
                  <div className="trending-section">
                    <label className="input-label" style={{ marginTop: '1rem' }}>Trending Topics</label>
                    <div className="category-chips">
                      {categories.map((cat) => (
                        <button
                          key={cat.id}
                          type="button"
                          className={`category-chip ${selectedCategories.includes(cat.id) ? 'active' : ''}`}
                          onClick={() => handleCategorySelect(cat.id)}
                        >
                          <span className="category-icon">{cat.icon}</span>
                          {cat.label}
                        </button>
                      ))}
                    </div>

                    {/* Loading State */}
                    {loadingTopics && (
                      <div className="suggestions-loading">
                        <span className="loading-dot"></span>
                        <span className="loading-dot"></span>
                        <span className="loading-dot"></span>
                      </div>
                    )}

                    {/* Error State */}
                    {topicsError && (
                      <div className="topics-error">{topicsError}</div>
                    )}

                    {/* Topic Suggestions */}
                    {suggestedTopics.length > 0 && (
                      <div className="topic-suggestions">
                        {suggestedTopics.map((suggestion, idx) => (
                          <div
                            key={idx}
                            className={`topic-suggestion ${selectedSuggestion === suggestion ? 'selected' : ''}`}
                            onClick={() => {
                              console.log('Clicked:', suggestion);
                              setSelectedSuggestion(suggestion);
                            }}
                          >
                            {suggestion}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Apply Button - always visible */}
                    <button
                      type="button"
                      className={`apply-suggestion-btn ${!selectedSuggestion ? 'disabled' : ''}`}
                      onClick={(e) => handleApplySuggestion(e)}
                      disabled={!selectedSuggestion}
                    >
                      {selectedSuggestion && selectedSuggestion.startsWith('Trending ') && selectedSuggestion.endsWith(' News')
                        ? 'Find Headlines'
                        : selectedSuggestion
                          ? `Use Topic: ${selectedSuggestion.length > 25 ? selectedSuggestion.substring(0, 25) + '...' : selectedSuggestion}`
                          : 'Select a category first'
                      }
                    </button>
                  </div>
                )}
              </div>
            ) : (
              /* Paste Text Input */
              <div className="input-group">
                <label className="input-label">Title (optional)</label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    className="topic-input"
                    placeholder="e.g. My Article Title"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    disabled={isGenerating || storyPlan !== null}
                  />
                </div>
                <label className="input-label" style={{ marginTop: '1rem' }}>Paste Your Content</label>
                <textarea
                  className="paste-textarea"
                  placeholder="Paste your article, notes, or any text here. AI will extract key facts and create story slides..."
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  disabled={isGenerating || storyPlan !== null}
                  rows={6}
                />
              </div>
            )}

            {/* Options Row */}
            <div className="options-section">
              <label className="input-label">Options</label>
              <div className="filter-row">
                <CustomDropdown
                  label="Slides"
                  value={`${numSlides}`}
                  options={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => ({ label: `${n} Slides`, value: n }))}
                  onSelect={setNumSlides}
                  disabled={isGenerating || storyPlan !== null}
                />


              </div>
            </div>

            {/* Generate Button */}
            {!storyPlan && !isGenerating ? (
              <button type="submit" className="generate-btn" disabled={!topic}>
                <span className="btn-content">Start Research</span>
                <div className="btn-glow"></div>
              </button>
            ) : isGenerating && generatingPhase === 'research' ? (
              <div className="sidebar-button-row">
                <button type="button" className="generate-btn" disabled>
                  <span className="btn-content">
                    <span className="btn-spinner"></span>
                    Researching...
                  </span>
                </button>
                <button
                  type="button"
                  className="sidebar-btn cancel"
                  onClick={() => {
                    setIsGenerating(false);
                    setGeneratingPhase(null);
                    setStoryPlan(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            ) : isGenerating && generatingPhase === 'images' ? (
              <button type="button" className="generate-btn generating-images" disabled>
                <span className="btn-content">
                  <span className="btn-spinner"></span>
                  Slide {currentGeneratingSlide} of {expectedSlides}
                </span>
              </button>
            ) : (
              <div className="sidebar-button-row">
                <button
                  type="button"
                  className="sidebar-btn cancel"
                  onClick={() => setStoryPlan(null)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="sidebar-btn reset"
                  onClick={() => {
                    setStoryPlan(null);
                    setTopic('');
                    setNumSlides(5);
                    setAesthetic('Cinematic');
                  }}
                >
                  Reset
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Footer */}

      </aside>

      {/* Collapsible Research Panel (shows when research is available) */}
      {completedResearch && !isGenerating && (
        <>
          <button
            className={`research-toggle ${researchCollapsed ? '' : 'expanded'}`}
            onClick={() => setResearchCollapsed(!researchCollapsed)}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M6 4L10 8L6 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <div className={`research-panel ${researchCollapsed ? 'collapsed' : 'expanded'}`}>
            <div className="research-panel-content">
              <div className="research-panel-header">
                <h3>Edit & Regenerate</h3>
                <span className="research-topic">{completedResearch.topic}</span>
              </div>

              <div className="research-panel-section">
                <label>Art Style</label>
                <p
                  contentEditable
                  suppressContentEditableWarning
                  onBlur={(e) => setCompletedResearch({
                    ...completedResearch,
                    aesthetic: { ...completedResearch.aesthetic, art_style: e.target.innerText }
                  })}
                  className="editable-research-field"
                >
                  {completedResearch.aesthetic?.art_style}
                </p>
              </div>

              <div className="research-panel-section">
                <label>Slides (click to edit)</label>
                {completedResearch.slides?.map((slide, idx) => (
                  <div key={idx} className="research-slide-item editable">
                    <span className="slide-num">{slide.slide_number}</span>
                    <div>
                      <strong
                        contentEditable
                        suppressContentEditableWarning
                        onBlur={(e) => handleEditCompletedResearch('title', e.target.innerText, idx)}
                      >
                        {slide.title}
                      </strong>
                      <p
                        contentEditable
                        suppressContentEditableWarning
                        onBlur={(e) => handleEditCompletedResearch('key_fact', e.target.innerText, idx)}
                      >
                        {slide.key_fact}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {completedResearch.sources?.length > 0 && (
                <div className="research-panel-section">
                  <label>Sources</label>
                  {completedResearch.sources.slice(0, 5).map((src, idx) => (
                    <a key={idx} href={src.url} target="_blank" rel="noopener noreferrer" className="research-source-link">
                      {src.title}
                    </a>
                  ))}
                </div>
              )}

              <button className="regenerate-btn" onClick={handleRegenerateImages}>
                Regenerate Images
              </button>
            </div>
          </div>
        </>
      )}

      {/* Main Content Area */}
      <main className="main-content">
        {/* REVIEW MODE */}
        {storyPlan && !generatedImages.length && !isGenerating ? (
          <div className="review-container">
            <div className="review-header">
              <h2>Research Phase Complete</h2>
              <p>Review the plan and select a style below.</p>
            </div>

            <div className="aesthetic-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3>Visual Aesthetic</h3>


              </div>

              <div className="style-grid">
                <div className="style-item">
                  <label>ART STYLE PROMPT</label>
                  <p
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) => handleEditAesthetic('art_style', e.target.innerText)}
                    className="editable-field"
                  >
                    {storyPlan.aesthetic.art_style}
                  </p>
                </div>
                <div className="style-item">
                  <label>COLOR PALETTE</label>
                  <p
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) => handleEditAesthetic('color_palette', e.target.innerText)}
                    className="editable-field"
                  >
                    {storyPlan.aesthetic.color_palette}
                  </p>
                </div>
                <div className="style-item">
                  <label>MOOD / LIGHTING</label>
                  <p
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) => handleEditAesthetic('lighting', e.target.innerText)}
                    className="editable-field"
                  >
                    {storyPlan.aesthetic.lighting}
                  </p>
                </div>
              </div>
              <p className="edit-hint">Click any field to edit</p>
            </div>

            <div className="slides-preview">
              <h3>Story Slides</h3>
              {storyPlan.slides.map((slide, index) => (
                <div key={slide.slide_number} className="slide-row">
                  <div className="slide-number">{slide.slide_number}</div>
                  <div className="slide-content-preview">
                    <h4
                      contentEditable
                      suppressContentEditableWarning
                      onBlur={(e) => handleEditSlide(index, 'title', e.target.innerText)}
                      className="editable-field"
                    >
                      {slide.title}
                    </h4>
                    <label className="field-label">Key Fact</label>
                    <p
                      contentEditable
                      suppressContentEditableWarning
                      onBlur={(e) => handleEditSlide(index, 'key_fact', e.target.innerText)}
                      className="editable-field"
                    >
                      {slide.key_fact}
                    </p>
                    <label className="field-label">Visual Description</label>
                    <p
                      contentEditable
                      suppressContentEditableWarning
                      onBlur={(e) => handleEditSlide(index, 'visual_description', e.target.innerText)}
                      className="editable-field visual-desc"
                    >
                      {slide.visual_description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Caption Section */}
            {storyPlan.caption && (
              <div className="caption-edit-section">
                <h3>Story Caption</h3>
                <p
                  contentEditable
                  suppressContentEditableWarning
                  onBlur={(e) => handleEditCaption(e.target.innerText)}
                  className="editable-field caption-field"
                >
                  {storyPlan.caption}
                </p>
                <div className="hashtags-edit">
                  {storyPlan.hashtags?.map((tag, i) => (
                    <span key={i} className="hashtag-pill">#{tag}</span>
                  ))}
                </div>
                <p className="edit-hint">Click caption to edit</p>
              </div>
            )}

            {/* Sources Section */}
            {storyPlan.sources && storyPlan.sources.length > 0 && (
              <div className="sources-section">
                <h3>Research Sources</h3>
                <div className="sources-list">
                  {storyPlan.sources.map((source, index) => (
                    <a
                      key={index}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-item"
                    >
                      <span className="source-number">{index + 1}</span>
                      <span className="source-title">{source.title}</span>
                    </a>
                  ))}
                </div>
              </div>
            )}

            <div className="action-buttons" style={{ alignItems: 'center', justifyContent: 'flex-end' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div className="final-style-selector" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.9rem', color: '#aaa' }}>Style:</label>
                  <select
                    value={aesthetic}
                    onChange={(e) => {
                      setAesthetic(e.target.value);
                      handleEditAesthetic('art_style', e.target.value + ' style');
                    }}
                    style={{
                      background: '#222',
                      border: '1px solid #444',
                      color: 'white',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      fontSize: '1rem',
                      cursor: 'pointer',
                      outline: 'none'
                    }}
                  >
                    {aesthetics.map(style => (
                      <option key={style} value={style}>{style}</option>
                    ))}
                  </select>
                </div>

                <button className="btn-primary" onClick={handleConfirmPlan}>
                  Generate Images →
                </button>
              </div>
            </div>
          </div>
        ) : isGenerating ? (
          <div className="generation-live">
            {generatingPhase === 'images' ? (
              <div className="live-generation-view">
                {/* Current slide being generated */}
                {generatingSlides.length > 0 && currentGeneratingSlide > 0 && (
                  <div className="current-slide-info">
                    <div className="slide-progress-header">
                      <span className="generating-label">Generating Slide {currentGeneratingSlide} of {expectedSlides}</span>
                    </div>

                    {generatingSlides[currentGeneratingSlide - 1] && (
                      <div className="generating-slide-card">
                        <div className="slide-number-badge">{currentGeneratingSlide}</div>
                        <h2 className="generating-slide-title">
                          {generatingSlides[currentGeneratingSlide - 1].title}
                        </h2>
                        <p className="generating-slide-fact">
                          {generatingSlides[currentGeneratingSlide - 1].key_fact}
                        </p>
                        <div className="generating-slide-visual">
                          <span className="visual-label">Visual:</span>
                          <p>{generatingSlides[currentGeneratingSlide - 1].visual_description}</p>
                        </div>
                      </div>
                    )}

                    {/* Slide queue preview */}
                    <div className="slide-queue">
                      {generatingSlides.map((slide, idx) => (
                        <div
                          key={idx}
                          className={`queue-dot ${idx + 1 < currentGeneratingSlide ? 'done' : ''} ${idx + 1 === currentGeneratingSlide ? 'active' : ''}`}
                        >
                          {idx + 1}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="research-progress">
                <div className="research-spinner"></div>
                <h3>Researching "{topic}"</h3>
                <p>Finding facts and planning slides...</p>
              </div>
            )}
          </div>
        ) : (
          <div className="boards-container">
            {/* Tabs */}
            <div className="boards-tabs">
              <button
                className={`board-tab ${activeTab === 'research' ? 'active' : ''}`}
                onClick={() => setActiveTab('research')}
              >
                Research
                {savedResearch.length > 0 && <span className="tab-count">{savedResearch.length}</span>}
              </button>
              <button
                className={`board-tab ${activeTab === 'images' ? 'active' : ''}`}
                onClick={() => setActiveTab('images')}
              >
                Images
                {savedImageBoards.length > 0 && <span className="tab-count">{savedImageBoards.length}</span>}
              </button>
            </div>

            {/* Content */}
            {activeTab === 'images' ? (
              savedImageBoards.length === 0 ? (
                <div className="empty-state">
                  <h2>No Images Yet</h2>
                  <p>Enter a topic on the left to generate your first story.</p>
                </div>
              ) : selectedBoard && selectedBoard.images ? (
                <div className="board-detail">
                  <div className="board-detail-header">
                    <button className="back-btn" onClick={() => setSelectedBoard(null)}>
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M12 4L6 10L12 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      Back
                    </button>
                    <h2>{selectedBoard.topic}</h2>
                    <div className="board-detail-actions">
                      <span className="board-detail-count">{selectedBoard.images.length} images</span>
                      <button className="download-all-btn" onClick={() => handleDownloadAll(selectedBoard.images)}>
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                          <path d="M8 2v8m0 0l-3-3m3 3l3-3M2 12v1a1 1 0 001 1h10a1 1 0 001-1v-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Download All
                      </button>
                    </div>
                  </div>

                  <div className="pinterest-grid">
                    {selectedBoard.images.map((img, idx) => (
                      <div key={idx} className="grid-item">
                        <img src={img} alt="" onClick={() => setSelectedImage({ src: img, idx, board: selectedBoard })} />
                        <div className="grid-overlay" onClick={() => setSelectedImage({ src: img, idx, board: selectedBoard })}>
                          <h3>Slide {idx + 1}</h3>
                        </div>
                        <button
                          className="grid-download-btn"
                          onClick={(e) => { e.stopPropagation(); handleDownloadImage(img, idx); }}
                        >
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                            <path d="M8 2v8m0 0l-3-3m3 3l3-3M2 12v1a1 1 0 001 1h10a1 1 0 001-1v-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="boards-grid">
                  {savedImageBoards.map((board) => (
                    <div key={board.id} className="board-card" onClick={() => setSelectedBoard(board)}>
                      <div className="board-stack-preview">
                        {board.images.slice(0, 3).map((img, idx) => (
                          <img key={idx} src={img} alt="" className={`stack-img stack-${idx}`} />
                        ))}
                      </div>
                      <div className="board-info">
                        <h3>{board.topic}</h3>
                        <p>{board.images.length} images</p>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              savedResearch.length === 0 ? (
                <div className="empty-state">
                  <h2>No Research Yet</h2>
                  <p>Your research will be saved here after generating stories.</p>
                </div>
              ) : selectedResearchBoard ? (
                <div className="research-detail">
                  <div className="board-detail-header">
                    <button className="back-btn" onClick={() => setSelectedResearchBoard(null)}>
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                        <path d="M12 4L6 10L12 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      Back
                    </button>
                    <h2>{selectedResearchBoard.topic}</h2>
                    <button
                      className="download-all-btn"
                      onClick={() => handleRegenerateImages(selectedResearchBoard)}
                    >
                      Generate Images
                    </button>
                  </div>

                  <div className="research-detail-content">
                    <div className="research-detail-section">
                      <label>Art Style</label>
                      <p>{selectedResearchBoard.aesthetic?.art_style}</p>
                    </div>

                    <div className="research-detail-section">
                      <label>Color Palette</label>
                      <p>{selectedResearchBoard.aesthetic?.color_palette}</p>
                    </div>

                    <div className="research-detail-section">
                      <label>Slides</label>
                      <div className="research-detail-slides">
                        {selectedResearchBoard.slides?.map((slide, idx) => (
                          <div key={idx} className="research-detail-slide">
                            <div className="slide-header">
                              <span className="slide-num">{slide.slide_number}</span>
                              <h4>{slide.title}</h4>
                            </div>
                            <p className="slide-fact">{slide.key_fact}</p>
                            <p className="slide-visual">{slide.visual_description}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {selectedResearchBoard.caption && (
                      <div className="research-detail-section">
                        <label>Caption</label>
                        <p>{selectedResearchBoard.caption}</p>
                        <div className="hashtags-preview">
                          {selectedResearchBoard.hashtags?.map((tag, i) => (
                            <span key={i} className="hashtag-pill">#{tag}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedResearchBoard.sources?.length > 0 && (
                      <div className="research-detail-section">
                        <label>Sources ({selectedResearchBoard.sources.length})</label>
                        <div className="research-detail-sources">
                          {selectedResearchBoard.sources.map((src, idx) => (
                            <a key={idx} href={src.url} target="_blank" rel="noopener noreferrer" className="source-link">
                              {src.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="research-boards-grid">
                  {savedResearch.map((research) => (
                    <div
                      key={research.id}
                      className="research-board-card"
                      onClick={() => setSelectedResearchBoard(research)}
                    >
                      <div className="research-board-header">
                        <h3>{research.topic}</h3>
                        <span className="slide-count">{research.slides?.length} slides</span>
                      </div>
                      <p className="research-style">{research.aesthetic?.art_style}</p>
                      <div className="research-slides-preview">
                        {research.slides?.slice(0, 3).map((slide, idx) => (
                          <div key={idx} className="research-slide-preview">
                            <span>{slide.slide_number}.</span> {slide.title}
                          </div>
                        ))}
                        {research.slides?.length > 3 && (
                          <div className="research-slide-preview more">+{research.slides.length - 3} more</div>
                        )}
                      </div>
                      {research.sources?.length > 0 && (
                        <div className="research-sources-count">{research.sources.length} sources</div>
                      )}
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}
      </main>

      {/* Lightbox */}
      {selectedImage && (
        <div className="lightbox-overlay" onClick={() => setSelectedImage(null)}>
          <button className="close-btn">&times;</button>

          {/* Previous Button */}
          {selectedImage.idx > 0 && (
            <button
              className="lightbox-nav lightbox-prev"
              onClick={(e) => {
                e.stopPropagation();
                const images = selectedImage.board?.images || generatedImages;
                const newIdx = selectedImage.idx - 1;
                setSelectedImage({ src: images[newIdx], idx: newIdx, board: selectedImage.board });
              }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          )}

          {/* Next Button */}
          {selectedImage.idx < (selectedImage.board?.images?.length || generatedImages.length) - 1 && (
            <button
              className="lightbox-nav lightbox-next"
              onClick={(e) => {
                e.stopPropagation();
                const images = selectedImage.board?.images || generatedImages;
                const newIdx = selectedImage.idx + 1;
                setSelectedImage({ src: images[newIdx], idx: newIdx, board: selectedImage.board });
              }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          )}

          <div className="lightbox-content" onClick={e => e.stopPropagation()}>
            <div className="lightbox-image-container">
              <img src={selectedImage.src} className="lightbox-image" alt="" />
            </div>
            <div className="lightbox-details">
              <div className="lightbox-meta">
                <span>{selectedImage.idx + 1} of {selectedImage.board?.images?.length || generatedImages.length}</span>
                <span>•</span>
                <span>Generated by AI</span>
              </div>
              <h2>{selectedImage.board?.slides?.[selectedImage.idx]?.title || generatedSlides[selectedImage.idx]?.title || topic}</h2>

              {/* Overall Story Caption */}
              {(selectedImage.board?.caption || storyCaption) && (
                <div className="caption-section">
                  <label className="caption-label">Story Caption</label>
                  <p className="caption-text">{selectedImage.board?.caption || storyCaption}</p>
                </div>
              )}

              {/* Hashtags */}
              {((selectedImage.board?.hashtags || storyHashtags)?.length > 0) && (
                <div className="hashtags-section">
                  <div className="hashtags-list">
                    {(selectedImage.board?.hashtags || storyHashtags).map((tag, i) => (
                      <span key={i} className="hashtag">#{tag}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="lightbox-actions">
                <button
                  className="overlay-btn copy-btn"
                  onClick={() => {
                    const caption = selectedImage.board?.caption || storyCaption;
                    const hashtags = selectedImage.board?.hashtags || storyHashtags;
                    const text = caption
                      ? `${caption}\n\n${hashtags?.map(t => '#' + t).join(' ') || ''}`
                      : '';
                    navigator.clipboard.writeText(text);
                    alert('Caption copied!');
                  }}
                >
                  Copy Caption
                </button>
                <button
                  className="overlay-btn"
                  onClick={() => handleDownloadImage(selectedImage.src, selectedImage.idx)}
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

function CustomDropdown({ label, value, options, onSelect, disabled, icon }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [dropdownRef]);

  return (
    <div className="custom-dropdown" ref={dropdownRef}>
      <div
        className={`dropdown-trigger ${isOpen ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        {icon && <span className="dropdown-icon">{icon}</span>}
        <div className="dropdown-content">
          <span className="dropdown-label">{label}</span>
          <span className="dropdown-value">{value}</span>
        </div>
        <span className="dropdown-arrow">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
      </div>

      {isOpen && (
        <div className="dropdown-menu">
          {options.map((opt) => (
            <div
              key={opt.label}
              className={`dropdown-item ${opt.value === value || opt.label === value ? 'selected' : ''}`}
              onClick={() => {
                onSelect(opt.value);
                setIsOpen(false);
              }}
            >
              {opt.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
