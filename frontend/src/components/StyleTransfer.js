import React, { useState } from 'react';
import axios from 'axios';

function StyleTransfer() {
  const [baseImage, setBaseImage] = useState(null);
  const [styleImage, setStyleImage] = useState(null);
  const [alpha, setAlpha] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [resultImage, setResultImage] = useState(null);
  const [error, setError] = useState(null);

  const handleBaseImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setBaseImage(e.target.files[0]);
    }
  };

  const handleStyleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setStyleImage(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResultImage(null);

    try {
      const formData = new FormData();
      formData.append('base_image', baseImage);
      formData.append('style_image', styleImage);
      formData.append('alpha', alpha);

      const response = await axios.post('/api/style-transfer', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResultImage(response.data.image);
      } else {
        setError('Failed to apply style transfer');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>🎨 Style Transfer</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Apply artistic styles from one image to another
      </p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="base_image">Base Image *</label>
          <div className="file-input-wrapper">
            <input
              id="base_image"
              type="file"
              accept="image/*"
              onChange={handleBaseImageChange}
              required
            />
            <label htmlFor="base_image" className="file-input-label">
              {baseImage ? baseImage.name : '📷 Choose Base Image'}
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="style_image">Style Image *</label>
          <div className="file-input-wrapper">
            <input
              id="style_image"
              type="file"
              accept="image/*"
              onChange={handleStyleImageChange}
              required
            />
            <label htmlFor="style_image" className="file-input-label">
              {styleImage ? styleImage.name : '🎨 Choose Style Image'}
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="alpha">Style Intensity: {alpha}</label>
          <input
            id="alpha"
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={alpha}
            onChange={(e) => setAlpha(parseFloat(e.target.value))}
          />
          <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
            Lower values preserve more of the base image, higher values apply more style
          </small>
        </div>

        <button type="submit" className="btn" disabled={loading || !baseImage || !styleImage}>
          {loading ? 'Applying Style...' : 'Apply Style Transfer'}
        </button>
      </form>

      {loading && <div className="loading">🎨 Applying style transfer... This may take a moment.</div>}

      {resultImage && (
        <div style={{ marginTop: '20px' }}>
          <h3>Result:</h3>
          <div className="image-item" style={{ maxWidth: '600px', margin: '20px auto' }}>
            <img src={resultImage} alt="Style Transfer Result" />
            <div className="image-overlay">Style Transfer Result</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StyleTransfer;
