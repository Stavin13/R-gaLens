import React, { useState } from 'react';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle } from 'lucide-react';

export default function Upload() {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('idle'); // idle, uploading, success, error
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setStatus('uploading');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/ingestion/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setStatus('success');
                setMessage(`Uploaded: ${data.filename}`);
            } else {
                setStatus('error');
                setMessage(`Error: ${data.detail}`);
            }
        } catch (error) {
            setStatus('error');
            setMessage(`Upload failed: ${error.message}`);
        }
    };

    return (
        <div className="card">
            <h2><UploadIcon className="icon" /> Ingestion</h2>
            <div className="upload-area">
                <input type="file" onChange={handleFileChange} accept=".pdf" />
                <button onClick={handleUpload} disabled={!file || status === 'uploading'}>
                    {status === 'uploading' ? 'Uploading...' : 'Upload PDF'}
                </button>
            </div>

            {status === 'success' && (
                <div className="status success">
                    <CheckCircle size={16} /> {message}
                </div>
            )}
            {status === 'error' && (
                <div className="status error">
                    <AlertCircle size={16} /> {message}
                </div>
            )}
        </div>
    );
}
