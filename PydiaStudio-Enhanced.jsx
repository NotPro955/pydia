import React, { useState } from 'react';
import { Instagram, Music, Linkedin, Menu, X, ChevronDown, Github } from 'lucide-react';

export default function PydiaStudio() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [url, setUrl] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selectedWebsite, setSelectedWebsite] = useState('github');

  const websites = [
    { id: 'linkedin', name: 'LinkedIn', icon: 'linkedin', color: 'from-blue-600 to-blue-700' },
    { id: 'github', name: 'GitHub', icon: 'github', color: 'from-gray-700 to-gray-800' },
    { id: 'wikipedia', name: 'Wikipedia', icon: 'wikipedia', color: 'from-blue-500 to-blue-600' },
    { id: 'twitter', name: 'Twitter', icon: 'twitter', color: 'from-black to-gray-800' },
    { id: 'instagram', name: 'Instagram', icon: 'instagram', color: 'from-pink-500 to-purple-600' },
  ];

  const renderIcon = (iconType) => {
    switch(iconType) {
      case 'linkedin':
        return <Linkedin size={16} />;
      case 'github':
        return <Github size={16} />;
      case 'instagram':
        return <Instagram size={16} />;
      case 'wikipedia':
        return '📖';
      case 'twitter':
        return '𝕏';
      default:
        return '○';
    }
  };

  const currentWebsite = websites.find(w => w.id === selectedWebsite) || websites[0];

  const handleGetStarted = () => {
    setCurrentPage('paste');
    setMobileMenuOpen(false);
  };

  const handleBackHome = () => {
    setCurrentPage('landing');
    setMobileMenuOpen(false);
  };

  // Navigation Component
  const Navigation = () => (
    <nav className="fixed top-0 w-full z-50 bg-white/95 backdrop-blur border-b border-gray-200/50">
      <div className="max-w-7xl mx-auto px-6 lg:px-12 py-4 flex justify-between items-center">
        <button onClick={handleBackHome} className="text-base lg:text-lg font-bold text-gray-900 hover:opacity-70 transition">
          PYDIA STUDIO®
        </button>
        
        {/* Desktop Menu */}
        <div className="hidden md:flex items-center gap-8">
          <button className="text-sm text-gray-700 hover:text-gray-900 transition font-medium">Home</button>
          <button className="text-sm text-gray-700 hover:text-gray-900 transition font-medium">About</button>
          <button className="text-sm text-gray-700 hover:text-gray-900 transition font-medium">Projects</button>
          <button className="text-sm text-gray-700 hover:text-gray-900 transition font-medium">Contact</button>
          <button
            onClick={handleGetStarted}
            className="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 rounded-full text-sm font-bold text-white transition transform hover:scale-105"
          >
            Get started
          </button>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden text-gray-900"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 px-6 py-4 space-y-3">
          <button className="block w-full text-left text-sm text-gray-700 hover:text-gray-900 font-medium py-2">Home</button>
          <button className="block w-full text-left text-sm text-gray-700 hover:text-gray-900 font-medium py-2">About</button>
          <button className="block w-full text-left text-sm text-gray-700 hover:text-gray-900 font-medium py-2">Projects</button>
          <button className="block w-full text-left text-sm text-gray-700 hover:text-gray-900 font-medium py-2">Contact</button>
          <button
            onClick={handleGetStarted}
            className="w-full px-5 py-2.5 bg-teal-600 hover:bg-teal-700 rounded-full text-sm font-bold text-white transition mt-4"
          >
            Get started
          </button>
        </div>
      )}
    </nav>
  );

  return (
    <div className="min-h-screen bg-white" onClick={() => setDropdownOpen(false)}>
      <Navigation />

      {/* Landing Page */}
      {currentPage === 'landing' && (
        <div className="relative min-h-screen text-white overflow-hidden pt-16">
          {/* Animated Background with Blobs and Gradients */}
          <div className="absolute inset-0 w-full h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 animate-bgShift">
            {/* Animated Blob 1 - Top Left */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-blue-500/30 to-cyan-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob"></div>
            
            {/* Animated Blob 2 - Top Right */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-500/30 to-pink-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob" style={{ animationDelay: '2s' }}></div>
            
            {/* Animated Blob 3 - Bottom Center */}
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-96 h-96 bg-gradient-to-tr from-cyan-500/30 to-blue-500/20 rounded-full mix-blend-screen filter blur-3xl animate-blob" style={{ animationDelay: '4s' }}></div>

            {/* Mesh Grid Background */}
            <svg className="absolute inset-0 w-full h-full opacity-20" preserveAspectRatio="none">
              <defs>
                <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
                  <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(100, 150, 255, 0.1)" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>

            {/* Animated Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent"></div>

            {/* Animated Light Streak - Left to Right */}
            <div className="absolute inset-0 overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-teal-500/10 to-transparent animate-lightStreak"></div>
            </div>

            {/* Animated Light Streaks - Diagonal */}
            <div className="absolute inset-0 overflow-hidden opacity-20">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-lightStreakDiag" style={{ animationDelay: '1s' }}></div>
              <div className="absolute top-1/3 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent animate-lightStreakDiag" style={{ animationDelay: '3s' }}></div>
              <div className="absolute top-2/3 left-0 w-full h-1 bg-gradient-to-r from-transparent via-teal-400 to-transparent animate-lightStreakDiag" style={{ animationDelay: '5s' }}></div>
            </div>
          </div>
          
          {/* Content */}
          <div className="relative h-screen flex items-center">
            <div className="w-full max-w-7xl mx-auto px-6 lg:px-12">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
                {/* Left Content - Only Button with Enhanced Animation */}
                <div className="space-y-8 animate-fadeInUpHero flex flex-col justify-center h-full">
                  <button
                    onClick={handleGetStarted}
                    className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700 rounded-full text-white font-bold text-base transition-all duration-300 transform hover:scale-110 active:scale-95 backdrop-blur-sm w-fit shadow-lg shadow-teal-500/50 hover:shadow-teal-500/80 hover:shadow-2xl animate-buttonGlow group"
                  >
                    <span className="relative">
                      Get started
                      <span className="absolute inset-0 rounded-full bg-gradient-to-r from-teal-400 to-cyan-400 opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-300 -z-10"></span>
                    </span>
                    <span className="text-xl group-hover:animate-bounce">↗</span>
                  </button>
                </div>

                {/* Right Content - 40% width */}
                <div className="hidden lg:flex flex-col items-end gap-8 justify-center animate-fadeInUpHero" style={{ animationDelay: '0.2s' }}>
                  {/* Social Icons with Floating Animation */}
                  <div className="flex gap-3 p-4 bg-white/10 backdrop-blur rounded-2xl border border-white/20 shadow-lg animate-float" style={{ animationDelay: '0.3s' }}>
                    <a href="#" title="Instagram" className="p-3 border border-white/30 rounded-full hover:bg-white/20 hover:border-white/50 transition-all duration-300 transform hover:scale-125 hover:rotate-6 group relative">
                      <Instagram size={20} className="text-white transition-all duration-300 group-hover:text-cyan-300" />
                      <div className="absolute inset-0 rounded-full bg-cyan-400/0 group-hover:bg-cyan-400/20 blur-xl transition-all duration-300 -z-10"></div>
                    </a>
                    <a href="#" title="Audio" className="p-3 border border-white/30 rounded-full hover:bg-white/20 hover:border-white/50 transition-all duration-300 transform hover:scale-125 hover:-rotate-6 group relative">
                      <Music size={20} className="text-white transition-all duration-300 group-hover:text-teal-300" />
                      <div className="absolute inset-0 rounded-full bg-teal-400/0 group-hover:bg-teal-400/20 blur-xl transition-all duration-300 -z-10"></div>
                    </a>
                    <a href="#" title="LinkedIn" className="p-3 border border-white/30 rounded-full hover:bg-white/20 hover:border-white/50 transition-all duration-300 transform hover:scale-125 hover:rotate-6 group relative">
                      <Linkedin size={20} className="text-white transition-all duration-300 group-hover:text-blue-300" />
                      <div className="absolute inset-0 rounded-full bg-blue-400/0 group-hover:bg-blue-400/20 blur-xl transition-all duration-300 -z-10"></div>
                    </a>
                  </div>

                  {/* Studio Card with Glassmorphism Glow */}
                  <div className="relative animate-float" style={{ animationDelay: '0.6s' }}>
                    <div className="absolute inset-0 bg-gradient-to-br from-teal-500/20 to-cyan-500/10 rounded-xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <div className="bg-gradient-to-br from-slate-700/60 to-slate-800/40 backdrop-blur border border-white/20 rounded-xl p-6 w-64 transform hover:scale-110 transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-teal-500/30 hover:border-teal-500/50 group relative">
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-teal-400/0 to-cyan-400/0 group-hover:from-teal-400/10 group-hover:to-cyan-400/10 transition-all duration-300 pointer-events-none"></div>
                      <div className="relative z-10">
                        <div className="flex items-center justify-center h-32 mb-4">
                          <div className="text-5xl animate-musicPulse">♪</div>
                        </div>
                        <p className="text-center text-sm font-bold text-white tracking-wide">PYDIA STUDIO</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* URL Paste Page */}
      {currentPage === 'paste' && (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900 pt-16">
          <div className="min-h-screen flex flex-col items-center justify-center px-6 lg:px-12 py-12">
            <div className="w-full max-w-3xl space-y-16 animate-fadeInUp">
              {/* Heading Section with Rolling Animation */}
              <div className="text-center space-y-6">
                <h1 className="text-5xl md:text-6xl lg:text-7xl font-black tracking-tight leading-tight overflow-hidden">
                  <span className="inline-block animate-rollInText">P</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.05s' }}>A</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.1s' }}>S</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.15s' }}>T</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.2s' }}>E</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.25s' }}>&nbsp;</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.3s' }}>Y</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.35s' }}>O</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.4s' }}>U</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.45s' }}>R</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.5s' }}>&nbsp;</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.55s' }}>U</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.6s' }}>R</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.65s' }}>L</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.7s' }}>&apos;</span>
                  <span className="inline-block animate-rollInText" style={{ animationDelay: '0.75s' }}>S</span>
                </h1>
              </div>

              {/* Input Section with Glow Animation */}
              <div className="space-y-6 animate-bounceIn">
                <div className="bg-gray-900 hover:bg-gray-800 rounded-full px-3 py-4 flex items-center gap-3 transition-all duration-300 border border-gray-700 focus-within:border-teal-500 focus-within:ring-2 focus-within:ring-teal-500/30 focus-within:shadow-lg focus-within:shadow-teal-500/20 focus-within:animate-pulse-glow group">
                  {/* Website Dropdown */}
                  <div className="relative">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setDropdownOpen(!dropdownOpen);
                      }}
                      className={`flex items-center justify-center gap-2 px-4 py-2 rounded-full transition-all duration-300 font-bold text-white text-sm bg-gradient-to-br ${currentWebsite.color} hover:shadow-lg hover:shadow-current hover:scale-110 active:scale-95`}
                    >
                      <span className="text-lg animate-pulse">{renderIcon(currentWebsite.icon)}</span>
                      <ChevronDown size={14} className={`transition-all duration-300 ${dropdownOpen ? 'rotate-180 scale-110' : ''}`} />
                    </button>

                    {/* Dropdown Menu */}
                    {dropdownOpen && (
                      <div className="absolute top-12 -left-4 bg-gray-800 border border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden backdrop-blur-sm animate-scaleIn" onClick={(e) => e.stopPropagation()}>
                        <div className="p-2">
                          {websites.map((site, idx) => (
                            <button
                              key={site.id}
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedWebsite(site.id);
                                setDropdownOpen(false);
                              }}
                              style={{ animationDelay: `${idx * 50}ms` }}
                              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 text-left group animate-slideIn ${
                                selectedWebsite === site.id
                                  ? 'bg-teal-600/30 border border-teal-500/50 scale-105'
                                  : 'hover:bg-gray-700/50 border border-transparent hover:scale-105'
                              }`}
                            >
                              <div className={`flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br ${site.color} text-white text-sm font-bold transition-all duration-300 group-hover:scale-125 group-hover:rotate-12`}>
                                {renderIcon(site.icon)}
                              </div>
                              <div className="flex flex-col">
                                <span className="text-white font-medium text-sm">{site.name}</span>
                              </div>
                              {selectedWebsite === site.id && (
                                <div className="ml-auto animate-ping">
                                  <div className="w-2 h-2 bg-teal-500 rounded-full"></div>
                                </div>
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* URL Input with Glow on Focus */}
                  <input
                    type="url"
                    placeholder={`Paste your ${currentWebsite.name} URL...`}
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="flex-1 bg-transparent text-white placeholder-gray-600 focus:outline-none text-lg font-light transition-all duration-300"
                  />
                </div>
              </div>

              {/* Services Grid Section - Horizontal Scroll with Bounce */}
              <div className="space-y-12 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
                <div className="relative overflow-hidden">
                  <div className="flex gap-12 lg:gap-16 animate-scroll" style={{ animationPlayState: 'running' }} onMouseEnter={(e) => e.currentTarget.style.animationPlayState = 'paused'} onMouseLeave={(e) => e.currentTarget.style.animationPlayState = 'running'}>
                    {/* Original set */}
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="flex-shrink-0 w-64 md:w-80 border-3 border-gray-400 rounded-2xl h-40 flex items-center justify-center hover:border-teal-500 transition-all duration-300 transform hover:scale-110 hover:-translate-y-2 hover:shadow-xl cursor-pointer bg-transparent group animate-float"
                        style={{ animationDelay: `${i * 0.1}s` }}
                      >
                        <span className="text-5xl md:text-6xl font-black tracking-widest text-transparent group-hover:drop-shadow-lg" style={{ WebkitTextStroke: '2px black' }}>SERVICES</span>
                      </div>
                    ))}
                    {/* Duplicate set 1 for infinite scroll */}
                    {[1, 2, 3].map((i) => (
                      <div
                        key={`duplicate-1-${i}`}
                        className="flex-shrink-0 w-64 md:w-80 border-3 border-gray-400 rounded-2xl h-40 flex items-center justify-center hover:border-teal-500 transition-all duration-300 transform hover:scale-110 hover:-translate-y-2 hover:shadow-xl cursor-pointer bg-transparent group animate-float"
                        style={{ animationDelay: `${i * 0.1}s` }}
                      >
                        <span className="text-5xl md:text-6xl font-black tracking-widest text-transparent group-hover:drop-shadow-lg" style={{ WebkitTextStroke: '2px black' }}>SERVICES</span>
                      </div>
                    ))}
                    {/* Duplicate set 2 for infinite scroll */}
                    {[1, 2, 3].map((i) => (
                      <div
                        key={`duplicate-2-${i}`}
                        className="flex-shrink-0 w-64 md:w-80 border-3 border-gray-400 rounded-2xl h-40 flex items-center justify-center hover:border-teal-500 transition-all duration-300 transform hover:scale-110 hover:-translate-y-2 hover:shadow-xl cursor-pointer bg-transparent group animate-float"
                        style={{ animationDelay: `${i * 0.1}s` }}
                      >
                        <span className="text-5xl md:text-6xl font-black tracking-widest text-transparent group-hover:drop-shadow-lg" style={{ WebkitTextStroke: '2px black' }}>SERVICES</span>
                      </div>
                    ))}
                    {/* Duplicate set 3 for infinite scroll */}
                    {[1, 2, 3].map((i) => (
                      <div
                        key={`duplicate-3-${i}`}
                        className="flex-shrink-0 w-64 md:w-80 border-3 border-gray-400 rounded-2xl h-40 flex items-center justify-center hover:border-teal-500 transition-all duration-300 transform hover:scale-110 hover:-translate-y-2 hover:shadow-xl cursor-pointer bg-transparent group animate-float"
                        style={{ animationDelay: `${i * 0.1}s` }}
                      >
                        <span className="text-5xl md:text-6xl font-black tracking-widest text-transparent group-hover:drop-shadow-lg" style={{ WebkitTextStroke: '2px black' }}>SERVICES</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Back Button with Hover Animation */}
              <div className="text-center pt-8">
                <button
                  onClick={handleBackHome}
                  className="inline-flex items-center gap-2 text-gray-600 hover:text-teal-500 font-semibold transition-all duration-300 transform hover:scale-110 hover:-translate-x-1 group"
                >
                  <span className="transform transition-all duration-300 group-hover:-translate-x-1">←</span>
                  <span>Back to home</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Animations */}
      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeInLeft {
          from {
            opacity: 0;
            transform: translateX(-30px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes scroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-200%);
          }
        }

        .animate-fadeInUp {
          animation: fadeInUp 0.7s ease-out;
        }

        .animate-fadeInLeft {
          animation: fadeInLeft 0.7s ease-out;
        }

        .animate-scroll {
          animation: scroll 80s linear infinite;
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.95);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-scaleIn {
          animation: scaleIn 0.3s ease-out;
        }

        .animate-slideIn {
          animation: slideIn 0.4s ease-out backwards;
        }

        @keyframes rollInText {
          from {
            opacity: 0;
            transform: rotateX(-90deg) translateY(-20px);
          }
          to {
            opacity: 1;
            transform: rotateX(0) translateY(0);
          }
        }

        .animate-rollInText {
          animation: rollInText 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        @keyframes bounceIn {
          0% {
            opacity: 0;
            transform: translateY(30px) scale(0.9);
          }
          50% {
            opacity: 1;
          }
          100% {
            transform: translateY(0) scale(1);
          }
        }

        .animate-bounceIn {
          animation: bounceIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }

        @keyframes shimmer {
          0% {
            background-position: -1000px 0;
          }
          100% {
            background-position: 1000px 0;
          }
        }

        .animate-shimmer {
          animation: shimmer 2s infinite;
          background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
          background-size: 1000px 100%;
        }

        @keyframes glow {
          0%, 100% {
            box-shadow: 0 0 5px rgba(20, 184, 166, 0.5);
          }
          50% {
            box-shadow: 0 0 20px rgba(20, 184, 166, 0.8);
          }
        }

        .animate-glow {
          animation: glow 2s ease-in-out infinite;
        }

        @keyframes pulse-glow {
          0%, 100% {
            box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.7);
          }
          50% {
            box-shadow: 0 0 0 10px rgba(20, 184, 166, 0);
          }
        }

        .animate-pulse-glow {
          animation: pulse-glow 2s infinite;
        }

        @keyframes flip {
          0% {
            transform: rotateY(0deg);
          }
          100% {
            transform: rotateY(360deg);
          }
        }

        .animate-flip {
          animation: flip 1s ease-in-out;
        }

        @keyframes wiggle {
          0%, 100% {
            transform: rotate(0deg);
          }
          25% {
            transform: rotate(-2deg);
          }
          75% {
            transform: rotate(2deg);
          }
        }

        .group:hover .animate-wiggle {
          animation: wiggle 0.5s ease-in-out;
        }

        @keyframes blob {
          0%, 100% {
            transform: translate(0, 0) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        @keyframes fadeInUpHero {
          from {
            opacity: 0;
            transform: translateY(40px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeInUpHero {
          animation: fadeInUpHero 0.8s ease-out;
        }

        @keyframes buttonGlow {
          0%, 100% {
            box-shadow: 0 0 20px rgba(20, 184, 166, 0.5), 0 0 40px rgba(20, 184, 166, 0.2);
          }
          50% {
            box-shadow: 0 0 30px rgba(20, 184, 166, 0.7), 0 0 60px rgba(20, 184, 166, 0.3);
          }
        }

        .animate-buttonGlow {
          animation: buttonGlow 3s ease-in-out infinite;
        }

        @keyframes lightStreak {
          0% {
            transform: translateX(-100%);
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
          100% {
            transform: translateX(100%);
            opacity: 0;
          }
        }

        .animate-lightStreak {
          animation: lightStreak 8s linear infinite;
        }

        @keyframes lightStreakDiag {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }

        .animate-lightStreakDiag {
          animation: lightStreakDiag 6s linear infinite;
        }

        @keyframes bgShift {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.02);
          }
        }

        .animate-bgShift {
          animation: bgShift 12s ease-in-out infinite;
        }

        @keyframes musicPulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.1);
            opacity: 0.8;
          }
        }

        .animate-musicPulse {
          animation: musicPulse 2s ease-in-out infinite;
        }

        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
        }

        input::placeholder {
          color: rgba(107, 114, 128, 0.6);
        }

        input:focus {
          color: white;
        }

        /* Smooth scrolling */
        html {
          scroll-behavior: smooth;
        }

        /* Remove scrollbar for webkit browsers */
        ::-webkit-scrollbar {
          width: 8px;
        }

        ::-webkit-scrollbar-track {
          background: transparent;
        }

        ::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 0, 0, 0.3);
        }
      `}</style>
    </div>
  );
}
