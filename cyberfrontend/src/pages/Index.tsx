import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import About from '@/components/About';
import DemoVideo from '@/components/DemoVideo';
import Gallery from '@/components/Gallery';
import Contact from '@/components/Contact';
import DownloadApp from '@/components/DownloadApp';
import Footer from '@/components/Footer';

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <About />
      <DemoVideo />
      <Gallery />
      <Contact />
      <DownloadApp />
      <Footer />
    </div>
  );
};

export default Index;
