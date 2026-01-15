export async function streamResearch(
  input: string,
  inputType: 'topic' | 'url',
  mode: 'gen-z' | 'analytical',
  callback: (event: any) => void
): Promise<void> {
  try {
    const response = await fetch('http://127.0.0.1:8008/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input, type: inputType, mode }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const json = JSON.parse(line.slice(6));
            callback(json);
          } catch (e) {
            console.error('Failed to parse event:', e);
          }
        }
      }
    }
  } catch (error) {
    callback({
      type: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
}

export async function fetchHistory(): Promise<{items: any[], total: number}> {
  try {
    const response = await fetch('http://127.0.0.1:8008/api/history');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch history:', error);
    return { items: [], total: 0 };
  }
}

export async function deleteResearch(id: string): Promise<boolean> {
  try {
    const response = await fetch(`http://127.0.0.1:8008/api/research/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return true;
  } catch (error) {
    console.error('Failed to delete research:', error);
    return false;
  }
}
