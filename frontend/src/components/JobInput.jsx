import { useState } from 'react';
import axios from 'axios';

const JobInput = ({ onJobSaved }) => {
  // State for the raw text phase
  const [rawText, setRawText] = useState("");
  const [loading, setLoading] = useState(false);

  // State for the "Review" phase (after AI parses it)
  const [parsedJob, setParsedJob] = useState(null);

  // 1. CALL THE AI PARSER
  const handleParse = async () => {
    setLoading(true);
    try {
      // Note: We send { raw_text: ... } because your Body(..., embed=True) expects it wrapped
      const res = await axios.post("http://localhost:8000/jobs/parse", { 
        raw_text: rawText 
      });
      setParsedJob(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to parse job.");
    }
    setLoading(false);
  };

  // 2. SAVE TO DATABASE
  const handleSave = async () => {
    try {
      const res = await axios.post("http://localhost:8000/jobs/", parsedJob);
      alert(`Job Saved! ID: ${res.data.id}`);
      
      // Notify the parent component (App.jsx) that we are done here
      if (onJobSaved) {
        onJobSaved(res.data.id);
      }
    } catch (err) {
      console.error(err);
      alert("Error saving job.");
    }
  };

  // Helper to update fields if user types in the form
  const handleChange = (e) => {
    setParsedJob({ ...parsedJob, [e.target.name]: e.target.value });
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px' }}>
      <h2>Step 2: Add a Job</h2>

      {/* VIEW 1: RAW TEXT INPUT */}
      {!parsedJob && (
        <div>
          <textarea 
            rows={10} 
            cols={50} 
            placeholder="Paste the Job Description here..."
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            style={{ width: '100%', padding: '10px' }}
          />
          <br />
          <button onClick={handleParse} disabled={loading} style={{ marginTop: '10px' }}>
            {loading ? "Analyzing..." : "Analyze Job"}
          </button>
        </div>
      )}

      {/* VIEW 2: REVIEW & EDIT FORM */}
      {parsedJob && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <h3>Review Details</h3>
          
          <label><strong>Company:</strong></label>
          <input name="company_name" value={parsedJob.company_name} onChange={handleChange} />

          <label><strong>Title:</strong></label>
          <input name="position_title" value={parsedJob.position_title} onChange={handleChange} />

          <label><strong>Salary:</strong></label>
          <input name="salary_range" value={parsedJob.salary_range} onChange={handleChange} />

          <label><strong>Summary:</strong></label>
          <textarea name="job_summary" rows={3} value={parsedJob.job_summary} onChange={handleChange} />

          <div style={{ marginTop: '10px' }}>
            <button onClick={handleSave} style={{ background: '#4CAF50', color: 'white' }}>
              Save & Continue
            </button>
            <button onClick={() => setParsedJob(null)} style={{ marginLeft: '10px' }}>
              Cancel (Paste Again)
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobInput;