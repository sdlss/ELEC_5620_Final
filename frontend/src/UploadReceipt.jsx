import React, { useState, useRef, useEffect } from 'react';

// Type definitions matching the API contract
// Note: In Create React App, we use PropTypes or JSDoc for type checking
// since TypeScript isn't configured by default

export default function UploadReceipt() {
  // Local state management
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [appState, setAppState] = useState('idle');
  
  const fileInputRef = useRef(null);

  // Clean up object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // File selection handler with validation
  const handleFileSelect = (event) => {
    const selectedFile = event.target.files?.[0];
    
    if (!selectedFile) {
      setFile(null);
      setPreviewUrl(null);
      setAppState('idle');
      setError(null);
      return;
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Unsupported file type. Please upload a JPG or PNG image.');
      setAppState('error');
      return;
    }

    // Validate file size (10 MB max)
    const maxSize = 10 * 1024 * 1024; // 10 MB in bytes
    if (selectedFile.size > maxSize) {
      setError('File is too large (max 10 MB).');
      setAppState('error');
      return;
    }

    // Clear previous errors and set new file
    setError(null);
    setFile(selectedFile);
    
    // Create preview URL
    const newPreviewUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(newPreviewUrl);
    setAppState('fileSelected');
  };

  // Form submission handler
  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!file) {
      setError('Please choose an image first.');
      setAppState('error');
      return;
    }

    setLoading(true);
    setAppState('uploading');
    setError(null);

    try {
      // Create FormData for multipart/form-data submission
      const formData = new FormData();
      formData.append('file', file);

      // Submit to OCR endpoint
      const response = await fetch('/api/ocr', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.ok) {
        setResult(data);
        setAppState('success');
      } else {
        setError('Something went wrong while processing the image.');
        setAppState('error');
      }
    } catch (err) {
      setError('Something went wrong while processing the image.');
      setAppState('error');
    } finally {
      setLoading(false);
    }
  };

  // Reset form to initial state
  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setAppState('idle');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div style={{ maxWidth: '768px', margin: '0 auto', padding: '24px' }}>
      {/* Page Title */}
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', textAlign: 'center', marginBottom: '24px' }}>
        Upload a receipt
      </h1>

      {/* File Selection Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* File Input */}
        <div>
          <label htmlFor="file-input" style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            Choose an image file
          </label>
          <input
            ref={fileInputRef}
            id="file-input"
            type="file"
            accept="image/png,image/jpeg"
            onChange={handleFileSelect}
            aria-label="Receipt image"
            style={{ 
              display: 'block', 
              width: '100%', 
              fontSize: '14px',
              padding: '8px',
              border: '1px solid #d1d5db',
              borderRadius: '6px'
            }}
          />
        </div>

        {/* Image Preview */}
        {previewUrl && (
          <div style={{ border: '1px solid #d1d5db', borderRadius: '8px', padding: '16px', backgroundColor: '#f9fafb' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>Preview</h3>
            <img
              src={previewUrl}
              alt="Selected receipt preview"
              style={{ maxHeight: '384px', width: '100%', objectFit: 'contain', borderRadius: '4px', border: '1px solid #d1d5db' }}
            />
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={appState === 'idle' || loading}
          aria-busy={loading}
          style={{
            width: '100%',
            backgroundColor: appState === 'idle' || loading ? '#9ca3af' : '#2563eb',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '8px',
            fontWeight: '500',
            border: 'none',
            cursor: appState === 'idle' || loading ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s'
          }}
        >
          {loading ? 'Processing…' : 'Extract fields'}
        </button>
      </form>

      {/* Error Banner */}
      {error && (
        <div 
          style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            padding: '16px',
            color: '#dc2626',
            marginTop: '24px'
          }}
          aria-live="polite"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Results Card */}
      {result && appState === 'success' && (
        <div style={{ border: '1px solid #d1d5db', borderRadius: '8px', padding: '24px', backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginTop: '24px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>Extracted Information</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {/* Item */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>Item</label>
              <p style={{ color: '#111827' }}>{result.item || '—'}</p>
            </div>

            {/* Price */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>Price</label>
              <p style={{ color: '#111827' }}>
                {result.price ? `${result.price.currency} ${result.price.value.toFixed(2)}` : '—'}
              </p>
            </div>

            {/* Date */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>Date</label>
              <p style={{ color: '#111827' }}>
                {result.date?.iso || result.date?.raw || '—'}
              </p>
            </div>

            {/* OCR Confidence */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>OCR confidence</label>
              <p style={{ color: '#111827' }}>{(result.confidence * 100).toFixed(1)}%</p>
            </div>

            {/* Raw OCR Text (Expandable) */}
            <details style={{ marginTop: '16px' }}>
              <summary style={{ cursor: 'pointer', fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>
                Raw OCR text
              </summary>
              <div style={{ marginTop: '8px', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '4px', border: '1px solid #d1d5db', fontSize: '14px', color: '#374151', whiteSpace: 'pre-wrap' }}>
                {result.rawText}
              </div>
            </details>
          </div>

          {/* Reset Button */}
          <button
            onClick={handleReset}
            style={{
              marginTop: '24px',
              width: '100%',
              backgroundColor: '#f3f4f6',
              color: '#374151',
              padding: '8px 16px',
              borderRadius: '8px',
              fontWeight: '500',
              border: 'none',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            Upload another receipt
          </button>
        </div>
      )}
    </div>
  );
}
