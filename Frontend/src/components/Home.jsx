import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExpand, faDownload } from '@fortawesome/free-solid-svg-icons';
import DOMPurify from 'dompurify';

const Home = () => {
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    const cachedImages = localStorage.getItem('images');
    if (cachedImages) {
      setImages(JSON.parse(cachedImages));
    } else{
    // Fetch images from the backend
    const fetchImages = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/chart/');
        const data = await response.json();
        setImages(data);
        localStorage.setItem('images', JSON.stringify(data));
      } catch (error) {
        console.error('Error fetching images:', error);
      }
    };

    fetchImages();
  }
  }, []);

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
      <div className="flex flex-col items-center justify-center min-h-screen pt-16 px-4 w-screen">
        <h1 className="text-3xl font-bold mb-8 mt-8 text-center">Advertisement Response Analysis</h1>
        
        <div className="w-full flex flex-col gap-8 px-4">
          {images.map((image, index) => (
            <div key={index} className="border p-6 rounded-lg shadow-lg flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-4 text-center">{image.title}</h2>
              
              <div className="flex flex-col md:flex-row w-full gap-6 items-center">
                <img src={`data:image/png;base64,${image.image}`} alt={image.title} className="w-full md:w-2/3 lg:w-1/2 rounded-lg mb-4 md:mb-0" />
                
                <div className="flex flex-col w-full md:w-1/4 lg:w-2/3">
                  <div className="border p-4 rounded-lg bg-gray-100 mb-4 text-sm text-black">
                  <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(image.summary.replace(/\n/g, '<br/>')) }} />
                  </div>
                  
                  <div className="flex justify-center flex-wrap gap-2">
                    <button
                      className="bg-blue-500 text-white px-4 py-2 rounded flex items-center mr-2 justify-center text-xs w-auto max-w-full md:max-w-1/3"
                      onClick={() => handleViewImage(image)}
                    >
                      <FontAwesomeIcon icon={faExpand} className="mr-2" />
                      View Full Size
                    </button>
                    <button
                      className="bg-green-500 text-white px-4 py-2 rounded flex items-center ml-2 justify-center text-xs w-auto max-w-full md:max-w-1/3"
                      onClick={() => handleDownloadImage(image)}
                    >
                      <FontAwesomeIcon icon={faDownload} className="mr-2" />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
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

export default Home;