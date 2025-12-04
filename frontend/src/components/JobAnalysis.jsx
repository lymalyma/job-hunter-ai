import { useState } from 'react';
import axios from 'axios';

const JobAnalysis = ({ jobId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [tailoredResume, setTailoredResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tailorLoading, setTailorLoading] = useState(false);

  // 1. CALL THE "CAREER COACH" AGENT
  const runAnalysis = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`http://localhost:8000/jobs/${jobId}/analyze`);
      setAnalysis(res.data);
    } catch (err) {
      console.error(err);
      alert("Analysis failed.");
    }
    setLoading(false);
  };

  // 2. CALL THE "RESUME WRITER" AGENT
  const runTailor = async () => {
    setTailorLoading(true);
    try {
      const res = await axios.post(`http://localhost:8000/jobs/${jobId}/tailor`);
      setTailoredResume(res.data);
    } catch (err) {
      console.error(err);
      alert("Tailoring failed.");
    }
    setTailorLoading(false);
  };

  // Helper for score color
  const getScoreColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'orange';
    return 'red';
  };

// ... imports and logic stay the same ...

  return (
    // FIX 1: Set the main container text to white (so "Step 3..." is visible)
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px', color: 'white' }}>
      <h2>Step 3: AI Career Strategy (Job ID: {jobId})</h2>

      {/* --- SECTION 1: STRATEGY (We keep this as a "Light Card" for contrast) --- */}
      {!analysis ? (
        <button onClick={runAnalysis} disabled={loading} style={{ padding: '10px 20px', fontSize: '16px' }}>
          {loading ? "Consulting Career Coach..." : "Run Strategy Analysis"}
        </button>
      ) : (
        // This box has a LIGHT background, so we MUST use DARK text inside it
        <div style={{ background: '#f9f9f9', color: '#333', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          <h3 style={{ marginTop: 0, color: '#333' }}>
            Match Score: <span style={{ color: getScoreColor(analysis.match_score) }}>{analysis.match_score}/100</span>
          </h3>
          <p><strong>Verdict:</strong> {analysis.recommendation}</p>
          
          <div style={{ background: '#fff', color: '#333', padding: '10px', borderLeft: '4px solid #007bff', marginBottom: '10px' }}>
            <strong>💡 Strategic Advice:</strong>
            <p style={{ marginTop: '5px' }}>{analysis.transferable_skills_advice}</p>
          </div>

          {analysis.missing_critical_skills.length > 0 && (
            <div style={{ color: '#d9534f' }}>
              <strong>⚠️ Missing Critical Skills:</strong>
              <ul>
                {analysis.missing_critical_skills.map(skill => <li key={skill}>{skill}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* --- SECTION 2: TAILORING --- */}
      {analysis && (
        <div style={{ borderTop: '2px dashed #ccc', paddingTop: '20px' }}>
          {!tailoredResume ? (
            <button onClick={runTailor} disabled={tailorLoading} style={{ padding: '10px 20px', background: '#6f42c1', color: 'white' }}>
              {tailorLoading ? "Rewriting Resume..." : "✨ Generate Tailored Resume"}
            </button>
          ) : (
            // FIX 2: We removed "color: #333" here. Now it inherits 'white' from the main container.
            <div>
              <h3>📝 Tailored Content</h3>
              
              <div style={{ marginBottom: '15px' }}>
                <label><strong>New Professional Summary:</strong></label>
                {/* FIX 3: The Textarea is a "Paper" (Light BG), so text inside must be Black */}
                <textarea 
                  readOnly 
                  style={{ 
                    width: '100%', 
                    padding: '10px', 
                    background: '#eef', // Light Blue Paper
                    color: '#000',      // Black Text
                    border: '1px solid #ccc',
                    marginTop: '5px'
                  }} 
                  rows={4}
                  value={tailoredResume.new_summary} 
                />
              </div>

              {/* FIX 4: The bullets are on the main background, so they will use the 'white' we set at the top */}
              <div style={{ color: '#e0e0e0' }}> {/* Light Grey for better readability */}
                <strong>Rewritten Experience:</strong>
                {Object.entries(tailoredResume.rewritten_experience).map(([company, bullets]) => (
                  <div key={company} style={{ marginTop: '10px' }}>
                    <strong style={{ color: '#fff', fontSize: '1.1em' }}>{company}</strong>
                    <ul style={{ paddingLeft: '20px' }}>
                      {bullets.map((b, i) => (
                        <li key={i} style={{ marginBottom: '5px' }}>{b}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobAnalysis;