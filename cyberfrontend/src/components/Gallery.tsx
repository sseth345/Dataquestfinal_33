import { useState } from 'react';
import { ZoomIn, X } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import dashboardScreenshot from '@/assets/dashboard-screenshot.jpg';
import mobileAppScreenshot from '@/assets/mobile-app-screenshot.jpg';
import networkSecurity from '@/assets/network-security.jpg';
import threatMap from '@/assets/threat-map.jpg';
import mobileapp from '@/assets/mobileapp.jpg';
import blockchain1 from '@/assets/blockchain1.jpg';
import blockchain2 from '@/assets/blockchain2.jpg';
import perf from '@/assets/perf.png';

import modelphoto from '@/assets/modelphoto.png';
import dataset from '@/assets/dataset.png';

const Gallery = () => {
  const [selectedImage, setSelectedImage] = useState<number | null>(null);

  const images = [
    {
      src: blockchain1,
      title: 'BlockChain',
      description: 'Decentralized blockchain technology with secure transaction processing and distributed ledger management'
    },
    {
      src: modelphoto,
      title: 'ML Model',
      description: 'Advanced machine learning algorithms for predictive analysis and intelligent automation'
    },
    {
      src: perf,
      title: 'Performance Metrics',
      description: 'Real-time system performance tracking with detailed analytics and optimization insights'
    },
    {
      src: dataset,
      title: 'Dataset',
      description: 'Comprehensive data collection and management with structured information processing'
    },
    {
      src: mobileapp,
      title: 'Mobile Application',
      description: 'Cross-platform mobile solution with intuitive user interface and seamless functionality'
    },
    {
      src: dashboardScreenshot,
      title: 'Comparision Analysis',
      description: 'Side-by-side data comparison with detailed statistical analysis and performance benchmarking'
    }
  ];

  const openLightbox = (index: number) => {
    setSelectedImage(index);
  };

  const closeLightbox = () => {
    setSelectedImage(null);
  };

  const navigateImage = (direction: 'prev' | 'next') => {
    if (selectedImage === null) return;
    
    if (direction === 'prev') {
      setSelectedImage(selectedImage === 0 ? images.length - 1 : selectedImage - 1);
    } else {
      setSelectedImage(selectedImage === images.length - 1 ? 0 : selectedImage + 1);
    }
  };

  return (
    <section id="gallery" className="py-20 bg-secondary/20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16 animate-fade-in">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="bg-gradient-primary bg-clip-text text-transparent">Screenshots</span>
            <span className="text-foreground"> & Interface</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Explore our intuitive interface designed for both security professionals and everyday users. 
            See how ThreatShield makes advanced cybersecurity accessible and actionable.
          </p>
        </div>

        {/* Gallery Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {images.map((image, index) => (
            <Card 
              key={index}
              className="group bg-gradient-card border-border/50 hover:border-cyber-blue/50 transition-all duration-300 hover:shadow-cyber cursor-pointer overflow-hidden animate-slide-up"
              style={{animationDelay: `${index * 0.1}s`}}
              onClick={() => openLightbox(index)}
            >
              <div className="relative aspect-video overflow-hidden">
                <img 
                  src={image.src} 
                  alt={image.title}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="p-3 bg-cyber-blue/20 backdrop-blur-md rounded-full border border-cyber-blue/50">
                    <ZoomIn className="h-6 w-6 text-cyber-blue" />
                  </div>
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-semibold text-foreground mb-2">{image.title}</h3>
                <p className="text-muted-foreground text-sm">{image.description}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Lightbox */}
        {selectedImage !== null && (
          <div className="fixed inset-0 z-50 bg-background/90 backdrop-blur-md flex items-center justify-center p-4">
            <div className="relative max-w-5xl max-h-[90vh] w-full">
              {/* Close Button */}
              <Button
                variant="ghost"
                size="sm"
                className="absolute top-4 right-4 z-10 bg-background/50 backdrop-blur-md hover:bg-background/80"
                onClick={closeLightbox}
              >
                <X className="h-6 w-6" />
              </Button>

              {/* Navigation Buttons */}
              <Button
                variant="ghost"
                size="sm"
                className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10 bg-background/50 backdrop-blur-md hover:bg-background/80"
                onClick={() => navigateImage('prev')}
              >
                ←
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-4 top-1/2 transform -translate-y-1/2 z-10 bg-background/50 backdrop-blur-md hover:bg-background/80"
                onClick={() => navigateImage('next')}
              >
                →
              </Button>

              {/* Image */}
              <div className="bg-gradient-card rounded-2xl border border-border/50 overflow-hidden shadow-card-custom">
                <img 
                  src={images[selectedImage].src} 
                  alt={images[selectedImage].title}
                  className="w-full h-auto max-h-[70vh] object-contain"
                />
                <div className="p-6">
                  <h3 className="text-2xl font-semibold text-foreground mb-2">
                    {images[selectedImage].title}
                  </h3>
                  <p className="text-muted-foreground">
                    {images[selectedImage].description}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Gallery;