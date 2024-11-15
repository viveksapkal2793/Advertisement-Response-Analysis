import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExpand, faDownload } from '@fortawesome/free-solid-svg-icons';
import DOMPurify from 'dompurify';

const Analyse = () => {
  const [combinations, setCombinations] = useState([]);
  const [selectedCombination, setSelectedCombination] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    const fetchCombinations = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/chartnames/');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setCombinations(data);
      } catch (error) {
        console.error('Error fetching combinations:', error);
      }
    };

    fetchCombinations();
  }, []);

  useEffect(() => { 
    const cachedAnalysis = localStorage.getItem('cachedAnalysis');
    if (cachedAnalysis) {
      // console.log(cachedAnalysis);
      setAnalysisResult(JSON.parse(cachedAnalysis));
    } 
  }, []);

  const getCookie = (name) => {
    const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return token;
  };

  const handleGetAnalysis = async () => {
    const csrfToken = getCookie('csrftoken'); 
    
      if (!selectedCombination) {
        console.error('No combination selected');
        return;
      }
        try {
        // console.log(selectedCombination);
        const response = await fetch('http://127.0.0.1:8000/api/customchart/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
          },
          
          body: JSON.stringify({ chart_type: selectedCombination}),
        });
        const data = await response.json();
        // console.log(data);
        setAnalysisResult(data[0]);
        localStorage.setItem('cachedAnalysis', JSON.stringify(data[0]));
        // console.log(analysisResult);
      } catch (error) {
        console.error('Error fetching analysis:', error);
      }
  };

  const handleViewImage = (image) => {
    setSelectedImage(image);
  };

  const handleDownloadImage = (image) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${image.image}`;
    link.download = image.title;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  

  return (
    <div>
      <Navbar />
      <div className="flex flex-col justify-center items-center min-h-screen pt-8 mx-auto w-screen">
        <div className="flex flex-col w-full px-4 justify-center items-center">
          <h1 className="text-3xl font-bold mb-4 mt-8 pt-4">Analyse Data</h1>
          <p>Select attributes to display charts and graphs.</p>
          
          <div className="flex flex-col items-center gap-4 mt-4">
            <select
              value={selectedCombination}
              onChange={(e) => setSelectedCombination(e.target.value)}
              className="border p-2 rounded"
            >
              <option value="" disabled>Select a combination</option>
              {combinations.map((combination) => (
                <option key={combination.value} value={combination.value}>
                  {combination.label}
                </option>
              ))}
            </select>
            
            <button
              onClick={handleGetAnalysis}
              className="bg-blue-500 text-white px-4 py-2 rounded"
            >
              Get Analysis
            </button>
          </div>
        </div>

        {analysisResult && (
          <div className="w-full flex flex-col gap-8 px-4 mt-8">
            <div className="border p-6 rounded-lg shadow-lg flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-4 text-center">{analysisResult.title}</h2>
              
              <div className="flex flex-col md:flex-row w-full gap-6 items-center">
                <img src={`data:image/png;base64,${analysisResult.image}`} alt={analysisResult.title} className="w-full md:w-2/3 lg:w-1/2 rounded-lg mb-4 md:mb-0" />
                
                <div className="flex flex-col w-full md:w-1/4 lg:w-2/3">
                  <div className="border p-4 rounded-lg bg-gray-100 mb-4 text-sm text-black">
                  {analysisResult.summary ? (
                      <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(analysisResult.summary.replace(/\n/g, '<br/>')) }} />
                    ) : (
                      <p>No summary available.</p>
                    )}
                  </div>
                  <div className="flex justify-center flex-wrap gap-2">
                    <button
                      className="bg-blue-500 text-white px-4 py-2 rounded flex items-center mr-2 justify-center text-xs w-auto max-w-full md:max-w-1/3"
                      onClick={() => handleViewImage(analysisResult)}
                    >
                      <FontAwesomeIcon icon={faExpand} className="mr-2" />
                      View Full Size
                    </button>
                    <button
                      className="bg-green-500 text-white px-4 py-2 rounded flex items-center ml-2 justify-center text-xs w-auto max-w-full md:max-w-1/3"
                      onClick={() => handleDownloadImage(analysisResult)}
                    >
                      <FontAwesomeIcon icon={faDownload} className="mr-2" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="relative">
            <button
              className="absolute top-0 right-0 bg-red-500 text-white px-4 py-2 rounded"
              onClick={() => setSelectedImage(null)}
            >
              Close
            </button>
            <img src={`data:image/png;base64,${selectedImage.image}`} alt={selectedImage.title} className="rounded-lg max-w-full max-h-full" />
          </div>
        </div>
      )}
    </div>
  );
};

export default Analyse;
