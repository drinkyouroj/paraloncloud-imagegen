import React, { useState } from 'react';
import axios from 'axios';

function ImageVariation() {
  const [image, setImage] = useState(null);
  const [model, setModel] = useState('dall-e-2');
  const [size, setSize] = useState('1024x1024');
  const [n, setN] = useState(1);
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState([]);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setImages([]);

    try {
      const formData = new FormData();
      formData.append('image', image);
      formData.append('model', model);
      formData.append('size', size);
      formData.append('n', n);

      const response = await axios.post('/api/variation', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setImages(response.data.images);
      } else {
        setError('Failed to create variations');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>🔄 Create Variations</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Generate creative variations of an existing image
      </p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="image">Image *</label>
          <div className="file-input-wrapper">
            <input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              required
            />
            <label htmlFor="image" className="file-input-label">
              {image ? image.name : '📷 Choose Image File'}
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="model">Model</label>
          <select
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="dall-e-2">DALL-E 2</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="size">Output Size</label>
          <select
            id="size"
            value={size}
            onChange={(e) => setSize(e.target.value)}
          >
            <option value="256x256">256x256</option>
            <option value="512x512">512x512</option>
            <option value="1024x1024">1024x1024</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="n">Number of Variations</label>
          <input
            id="n"
            type="number"
            min="1"
            max="10"
            value={n}
            onChange={(e) => setN(parseInt(e.target.value))}
          />
        </div>

        <button type="submit" className="btn" disabled={loading || !image}>
          {loading ? 'Creating Variations...' : 'Create Variations'}
        </button>
      </form>

      {loading && <div className="loading">🔄 Creating variations... This may take a moment.</div>}

      {images.length > 0 && (
        <div className="image-gallery">
          {images.map((image, index) => (
            <div key={index} className="image-item">
              <img src={image} alt={`Variation ${index + 1}`} />
              <div className="image-overlay">Variation {index + 1}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ImageVariation;
