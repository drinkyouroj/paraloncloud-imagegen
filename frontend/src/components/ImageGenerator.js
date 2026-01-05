import React, { useState } from 'react';
import axios from 'axios';

function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('dall-e-3');
  const [size, setSize] = useState('1024x1024');
  const [quality, setQuality] = useState('standard');
  const [n, setN] = useState(1);
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setImages([]);

    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('model', model);
      formData.append('size', size);
      formData.append('quality', quality);
      formData.append('n', n);

      const response = await axios.post('/api/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setImages(response.data.images);
      } else {
        setError('Failed to generate images');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>✨ Generate Images</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Create stunning images from text descriptions using AI
      </p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="prompt">Image Description *</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the image you want to generate... (e.g., 'A futuristic cityscape at sunset with flying cars')"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="model">Model</label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="dall-e-3">DALL-E 3</option>
            <option value="dall-e-2">DALL-E 2</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="size">Image Size</label>
          <select
            id="size"
            value={size}
            onChange={(e) => setSize(e.target.value)}
          >
            {model === 'dall-e-3' ? (
              <>
                <option value="1024x1024">1024x1024 (Square)</option>
                <option value="1792x1024">1792x1024 (Landscape)</option>
                <option value="1024x1792">1024x1792 (Portrait)</option>
              </>
            ) : (
              <>
                <option value="256x256">256x256</option>
                <option value="512x512">512x512</option>
                <option value="1024x1024">1024x1024</option>
              </>
            )}
          </select>
        </div>

        {model === 'dall-e-3' && (
          <div className="form-group">
            <label htmlFor="quality">Quality</label>
            <select
              id="quality"
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
            >
              <option value="standard">Standard</option>
              <option value="hd">HD</option>
            </select>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="n">Number of Images</label>
          <input
            id="n"
            type="number"
            min="1"
            max={model === 'dall-e-3' ? 1 : 10}
            value={n}
            onChange={(e) => setN(parseInt(e.target.value))}
          />
          {model === 'dall-e-3' && (
            <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
              DALL-E 3 only supports generating 1 image at a time
            </small>
          )}
        </div>

        <button type="submit" className="btn" disabled={loading || !prompt.trim()}>
          {loading ? 'Generating...' : 'Generate Image'}
        </button>
      </form>

      {loading && <div className="loading">✨ Creating your image... This may take a moment.</div>}

      {images.length > 0 && (
        <div className="image-gallery">
          {images.map((image, index) => (
            <div key={index} className="image-item">
              <img src={image} alt={`Generated ${index + 1}`} />
              <div className="image-overlay">Generated Image {index + 1}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ImageGenerator;
