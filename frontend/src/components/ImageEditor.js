import React, { useState } from 'react';
import axios from 'axios';

function ImageEditor() {
  const [image, setImage] = useState(null);
  const [mask, setMask] = useState(null);
  const [prompt, setPrompt] = useState('');
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

  const handleMaskChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setMask(e.target.files[0]);
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
      formData.append('prompt', prompt);
      formData.append('model', model);
      formData.append('size', size);
      formData.append('n', n);
      if (mask) {
        formData.append('mask', mask);
      }

      const response = await axios.post('/api/edit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setImages(response.data.images);
      } else {
        setError('Failed to edit image');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>✏️ Edit Images</h2>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Edit existing images by describing the changes you want to make
      </p>

      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="image">Image to Edit *</label>
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
          <label htmlFor="mask">Mask Image (Optional)</label>
          <div className="file-input-wrapper">
            <input
              id="mask"
              type="file"
              accept="image/*"
              onChange={handleMaskChange}
            />
            <label htmlFor="mask" className="file-input-label">
              {mask ? mask.name : '🎭 Choose Mask File (transparent areas indicate where to edit)'}
            </label>
          </div>
          <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
            A mask image with transparent areas indicates where edits should be applied
          </small>
        </div>

        <div className="form-group">
          <label htmlFor="prompt">Edit Description *</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the changes you want to make... (e.g., 'Add a rainbow in the sky')"
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

        <button type="submit" className="btn" disabled={loading || !image || !prompt.trim()}>
          {loading ? 'Editing...' : 'Edit Image'}
        </button>
      </form>

      {loading && <div className="loading">✏️ Editing your image... This may take a moment.</div>}

      {images.length > 0 && (
        <div className="image-gallery">
          {images.map((image, index) => (
            <div key={index} className="image-item">
              <img src={image} alt={`Edited ${index + 1}`} />
              <div className="image-overlay">Edited Image {index + 1}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ImageEditor;
