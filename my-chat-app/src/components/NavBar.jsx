import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const toggleMenu = () => setIsMenuOpen((prev) => !prev);
  const closeMenu = () => setIsMenuOpen(false);

  // Ensure logo and logo-name always navigate to home, even on mobile
  const handleLogoClick = (e) => {
    e.preventDefault();
    closeMenu();
    navigate('/');
  };

  return (
    <nav className="navbar">
      {/* Logo with fixed path */}
      <a href="/" className="nav-logo" onClick={handleLogoClick}>
        <img src="/assets/images/plotbuddy-navbar-logo.svg" alt="PlotBuddy" />
      </a>
      <a href="/" className="nav-logo-name" onClick={handleLogoClick}>
        <img src="/assets/images/plotbuddy-text-logo.svg" alt="PlotBuddy" />
      </a>
      <button 
        className="nav-menu-button" 
        onClick={toggleMenu}
        aria-label="Toggle menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          {isMenuOpen ? (
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          ) : (
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          )}
        </svg>
      </button>

      <div className={`nav-links ${isMenuOpen ? 'open' : ''}`} ref={menuRef}>
        <Link to="/" className="nav-link" onClick={closeMenu}>
          Home
        </Link>
        
        <Link 
          to="/create" 
          className="nav-button" 
          onClick={closeMenu}
          style={{ display: 'inline-block', textDecoration: 'none' }}
        >
          Create Story
        </Link>
        
        <Link to="/random-story" className="nav-link" onClick={closeMenu}>
          Random Story
        </Link>
        
        <Link to="/profile" className="nav-link" onClick={closeMenu}>
          My Profile
        </Link>
      </div>
    </nav>
  );
};

export default NavBar;
