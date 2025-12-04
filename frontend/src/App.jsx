import { useState } from 'react';
import ResumeUpload from './components/ResumeUpload';
import JobInput from './components/JobInput';
import JobAnalysis from './components/JobAnalysis'; // <--- Import

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [activeJobId, setActiveJobId] = useState(null);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Job Hunter AI 🤖</h1>
      
      {/* NAVIGATION TABS */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
        <button onClick={() => setCurrentStep(1)} style={navStyle(currentStep === 1)}>1. Resume</button>
        {' > '}
        <button onClick={() => setCurrentStep(2)} style={navStyle(currentStep === 2)}>2. Job Search</button>
        {' > '}
        <button disabled={!activeJobId} onClick={() => setCurrentStep(3)} style={navStyle(currentStep === 3)}>3. Strategy</button>
      </div>

      {currentStep === 1 && <ResumeUpload />}

      {currentStep === 2 && (
        <JobInput 
          onJobSaved={(jobId) => {
            setActiveJobId(jobId);
            setCurrentStep(3); // <--- Auto-advance to next step
          }} 
        />
      )}

      {currentStep === 3 && activeJobId && (
        <JobAnalysis jobId={activeJobId} />
      )}
    </div>
  );
}

// Simple style helper
const navStyle = (isActive) => ({
  fontWeight: isActive ? 'bold' : 'normal',
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontSize: '16px',
  color: isActive ? '#007bff' : '#666'
});

export default App;