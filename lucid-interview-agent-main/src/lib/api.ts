// API client for communicating with the backend

// Backend API base URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Authentication API
 */
export const AuthAPI = {
  // Register a new user
  register: async (userData: { email: string; password: string; full_name: string }) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    const data = await response.json();
    // Store token in local storage
    localStorage.setItem('token', data.access_token);
    return data;
  },
  
  // Login user
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email); // OAuth2 uses username field but we're using email
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    const data = await response.json();
    // Store token in local storage
    localStorage.setItem('token', data.access_token);
    return data;
  },
  
  // Logout user
  logout: () => {
    localStorage.removeItem('token');
  },
  
  // Get authentication token
  getToken: () => localStorage.getItem('token'),
  
  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return !!token;
  },
  
  // Get current user info
  getUserInfo: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      let errorDetail;
      try {
        // Try to parse as JSON
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || `Error ${response.status}`;
      } catch (e) {
        // If not valid JSON, use the raw text
        errorDetail = errorText || `Error ${response.status}`;
      }
      
      console.error(`User info fetch failed with status ${response.status}:`, errorDetail);
      throw new Error(`Failed to fetch user info: ${errorDetail}`);
    }
    
    return await response.json();
  },
  
  // Extract user info from JWT token (fallback)
  getUserInfoFromToken: () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    
    try {
      // Get the payload part of the JWT (second part)
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64).split('').map(c => {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join('')
      );
      
      const payload = JSON.parse(jsonPayload);
      
      // Basic user info from token
      return {
        id: parseInt(payload.sub),
        email: payload.email,
        full_name: payload.email.split('@')[0], // Fallback name if not in token
        is_active: true
      };
    } catch (e) {
      console.error("Failed to decode token:", e);
      return null;
    }
  },
};

/**
 * Interviews API
 */
export const InterviewsAPI = {
  // Create a new interview
  createInterview: async (interviewData: { 
    title: string;
    description?: string;
    interview_type: string;
    position: string;
    difficulty_level?: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/interviews/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AuthAPI.getToken()}`
      },
      body: JSON.stringify(interviewData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create interview');
    }
    
    return await response.json();
  },
  
  // Get all interviews for user
  getUserInterviews: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/interviews/`, {
        headers: {
          'Authorization': `Bearer ${AuthAPI.getToken()}`
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorDetail;
        try {
          // Try to parse as JSON
          const errorJson = JSON.parse(errorText);
          errorDetail = errorJson.detail || `Error ${response.status}`;
        } catch (e) {
          // If not valid JSON, use the raw text
          errorDetail = errorText || `Error ${response.status}`;
        }
        
        console.error(`Interview fetch failed with status ${response.status}:`, errorDetail);
        throw new Error(`Failed to fetch interviews: ${errorDetail}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error in getUserInterviews:", error);
      // Return empty array instead of throwing to prevent dashboard crash
      return [];
    }
  },
  
  // Get a specific interview
  getInterview: async (interviewId: number) => {
    const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}`, {
      headers: {
        'Authorization': `Bearer ${AuthAPI.getToken()}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch interview');
    }
    
    return await response.json();
  },
  
  // Start an interview
  startInterview: async (interviewId: number) => {
    const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}/start`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${AuthAPI.getToken()}`
      }
    });
    
    if (!response.ok) {
      console.log("***************************",response)
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start interview');
    }
    console.log("***************************",response)

    return await response.json();
  },
  
  // Submit a response
  submitResponse: async (data: {
    session_token: string;
    audio_data?: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/interviews/session/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${AuthAPI.getToken()}`
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit response');
    }
    
    return await response.json();
  },
  
  // Get interview results
  getInterviewResults: async (interviewId: number) => {
    const response = await fetch(`${API_BASE_URL}/interviews/${interviewId}/results`, {
      headers: {
        'Authorization': `Bearer ${AuthAPI.getToken()}`
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch interview results');
    }
    
    return await response.json();
  }
};

/**
 * WebSocket connection for real-time interview
 */
export class InterviewWebSocketConnection {
  private ws: WebSocket | null = null;
  private sessionToken: string;
  private callbacks: {
    onMessage?: (data: any) => void;
    onTranscript?: (text: string, confidence: number) => void;
    onError?: (error: any) => void;
    onClose?: () => void;
    onOpen?: () => void;
  } = {};
  private audioChunks: Blob[] = [];
  private chunkSequence = 0;
  private pingInterval: number | null = null;
  
  constructor(sessionToken: string) {
    this.sessionToken = sessionToken;
  }
  
  async connect(): Promise<this> {
    return new Promise((resolve, reject) => {
      try {
        // Fix the WebSocket URL format
        const wsUrl = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
        console.log(`Connecting to WebSocket at: ${wsUrl}/ws/interview/${this.sessionToken}`);
        
        // Connect to WebSocket
        this.ws = new WebSocket(`${wsUrl}/ws/interview/${this.sessionToken}`);
        
        // Set timeout for connection
        const connectionTimeout = setTimeout(() => {
          reject(new Error('WebSocket connection timeout'));
        }, 10000); // 10 second timeout
        
        this.ws.onopen = () => {
          console.log('WebSocket connected successfully');
          clearTimeout(connectionTimeout);
          this.startPingInterval();
          if (this.callbacks.onOpen) this.callbacks.onOpen();
          resolve(this);
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket connection error:', error);
          clearTimeout(connectionTimeout);
          reject(error);
        };
      } catch (error) {
        console.error('Error creating WebSocket:', error);
        reject(error);
      }
    });
    
    this.ws!.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (this.callbacks.onMessage) this.callbacks.onMessage(data);
        
        // Handle specific message types
        if (data.type === 'transcript_update' && this.callbacks.onTranscript) {
          this.callbacks.onTranscript(data.transcript, data.confidence);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.callbacks.onError) this.callbacks.onError(error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopPingInterval();
      if (this.callbacks.onClose) this.callbacks.onClose();
    };
    
    return this;
  }
  
  // Set callbacks
  on(event: 'message' | 'transcript' | 'error' | 'close' | 'open', callback: any) {
    if (event === 'message') this.callbacks.onMessage = callback;
    if (event === 'transcript') this.callbacks.onTranscript = callback;
    if (event === 'error') this.callbacks.onError = callback;
    if (event === 'close') this.callbacks.onClose = callback;
    if (event === 'open') this.callbacks.onOpen = callback;
    return this;
  }
  
  // Send audio chunk
  sendAudioChunk(audioBlob: Blob) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }
    
    // Add to audio chunks for later combining
    this.audioChunks.push(audioBlob);
    
    // Convert blob to base64
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Audio = (reader.result as string).split(',')[1];
      const message = {
        type: 'audio_chunk',
        audio_data: base64Audio,
        chunk_sequence: this.chunkSequence++
      };
      
      this.ws?.send(JSON.stringify(message));
    };
    reader.readAsDataURL(audioBlob);
  }
  
  // Send final audio
  async sendFinalAudio() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      return;
    }
    
    // Combine all audio chunks
    const completeAudio = new Blob(this.audioChunks, { type: 'audio/webm' });
    
    // Convert blob to base64
    const base64Audio = await this.blobToBase64(completeAudio);
    const message = {
      type: 'audio_final',
      audio_data: base64Audio
    };
    
    this.ws.send(JSON.stringify(message));
    this.audioChunks = []; // Reset audio chunks
  }
  
  // Helper to convert blob to base64
  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64Audio = (reader.result as string).split(',')[1];
        resolve(base64Audio);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }
  
  // Start ping interval to keep connection alive
  private startPingInterval() {
    this.pingInterval = window.setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'ping',
          timestamp: Date.now()
        }));
      }
    }, 30000); // Ping every 30 seconds
  }
  
  // Stop ping interval
  private stopPingInterval() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
  
  // Close connection
  close() {
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
