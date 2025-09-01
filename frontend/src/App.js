import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { useRazorpay } from "react-razorpay";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true
      });
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = (redirectUrl) => {
    // Use current frontend URL as redirect target
    const currentUrl = redirectUrl || window.location.origin;
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(currentUrl)}`;
    console.log('Redirecting to auth with redirect URL:', currentUrl);
    window.location.href = authUrl;
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, {
        withCredentials: true
      });
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  useEffect(() => {
    // Check for session_id in URL - could be in fragment (#) or query (?)
    const urlParams = new URLSearchParams(window.location.search);
    const fragment = window.location.hash;
    
    let sessionId = null;
    
    // Check query parameters first
    if (urlParams.has('session_id')) {
      sessionId = urlParams.get('session_id');
    }
    // Check URL fragment as fallback
    else if (fragment.includes('session_id=')) {
      sessionId = fragment.split('session_id=')[1].split('&')[0];
    }
    
    if (sessionId) {
      console.log('Found session_id:', sessionId);
      
      // Exchange session ID for user data - send as form data
      const formData = new FormData();
      formData.append('session_id', sessionId);
      
      axios.post(`${API}/auth/session`, formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        console.log('Session authentication successful:', response.data);
        setUser(response.data);
        setLoading(false);
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
        // Don't redirect automatically, let user navigate
      }).catch(error => {
        console.error('Session authentication failed:', error);
        console.error('Error details:', error.response?.data);
        setLoading(false);
      });
    } else {
      checkAuth();
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Auth Modal Component
const AuthModal = ({ onClose }) => {
  const [mode, setMode] = useState('register'); // 'register' or 'login'
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    thaparEmailPrefix: '',
    phone: '+91', // Default +91 prefix
    isFaculty: false,
    // Student fields
    branch: '',
    rollNumber: '',
    batch: '',
    // Faculty fields
    department: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const login = (redirectUrl) => {
    // Use current frontend URL as redirect target
    const currentUrl = redirectUrl || window.location.origin;
    const authUrl = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(currentUrl)}`;
    console.log('Redirecting to auth with redirect URL:', currentUrl);
    window.location.href = authUrl;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Check if user exists
      const formDataToSend = new FormData();
      formDataToSend.append('thapar_email_prefix', formData.thaparEmailPrefix);

      const response = await axios.post(`${API}/auth/check-user`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.exists) {
        // User exists, proceed to Emergent auth
        onClose();
        login();
      } else {
        setError('User not found in our database. Please register first with your Thapar email to create an account, then login.');
      }
    } catch (error) {
      console.error('Login check error:', error);
      setError('Failed to check user. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate required fields
      if (!formData.firstName || !formData.lastName || !formData.thaparEmailPrefix) {
        setError('Please fill in all required fields.');
        setLoading(false);
        return;
      }

      if (formData.isFaculty && !formData.department) {
        setError('Department is required for faculty.');
        setLoading(false);
        return;
      }

      if (!formData.isFaculty && (!formData.branch || !formData.rollNumber || !formData.batch)) {
        setError('Branch, roll number, and batch are required for students.');
        setLoading(false);
        return;
      }

      // Register user
      const registrationData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        thapar_email_prefix: formData.thaparEmailPrefix,
        is_faculty: formData.isFaculty,
        branch: formData.isFaculty ? null : formData.branch,
        roll_number: formData.isFaculty ? null : formData.rollNumber,
        batch: formData.isFaculty ? null : formData.batch,
        department: formData.isFaculty ? formData.department : null
      };

      await axios.post(`${API}/auth/register`, registrationData);

      // Registration successful, proceed to Emergent auth
      onClose();
      login();
    } catch (error) {
      console.error('Registration error:', error);
      if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">
              {mode === 'register' ? 'Register' : 'Login'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {mode === 'register' ? (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">First Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.firstName}
                    onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Last Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.lastName}
                    onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Thapar Email *</label>
                <div className="flex">
                  <input
                    type="text"
                    required
                    value={formData.thaparEmailPrefix}
                    onChange={(e) => setFormData({...formData, thaparEmailPrefix: e.target.value})}
                    placeholder="username"
                    className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                  />
                  <span className="bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg px-3 py-2 text-gray-600">
                    @thapar.edu
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">Enter only the part before @thapar.edu</p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isFaculty"
                  checked={formData.isFaculty}
                  onChange={(e) => setFormData({...formData, isFaculty: e.target.checked})}
                  className="mr-2"
                />
                <label htmlFor="isFaculty" className="text-sm font-medium">I am a faculty member</label>
              </div>

              {formData.isFaculty ? (
                <div>
                  <label className="block text-sm font-medium mb-1">Department *</label>
                  <input
                    type="text"
                    required
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                    placeholder="e.g., Computer Science"
                  />
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Branch *</label>
                    <input
                      type="text"
                      required
                      value={formData.branch}
                      onChange={(e) => setFormData({...formData, branch: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                      placeholder="e.g., Computer Engineering"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Roll Number *</label>
                      <input
                        type="text"
                        required
                        value={formData.rollNumber}
                        onChange={(e) => setFormData({...formData, rollNumber: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                        placeholder="e.g., 102103456"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Batch *</label>
                      <input
                        type="text"
                        required
                        value={formData.batch}
                        onChange={(e) => setFormData({...formData, batch: e.target.value})}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                        placeholder="e.g., 2021-2025"
                      />
                    </div>
                  </div>
                </>
              )}
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:bg-gray-400"
              >
                {loading ? 'Registering...' : 'Register'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setMode('login')}
                  className="text-black hover:underline"
                >
                  Already a user? Login
                </button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Thapar Email *</label>
                <div className="flex">
                  <input
                    type="text"
                    required
                    value={formData.thaparEmailPrefix}
                    onChange={(e) => setFormData({...formData, thaparEmailPrefix: e.target.value})}
                    placeholder="username"
                    className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                  />
                  <span className="bg-gray-100 border border-l-0 border-gray-300 rounded-r-lg px-3 py-2 text-gray-600">
                    @thapar.edu
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">Enter only the part before @thapar.edu</p>
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:bg-gray-400"
              >
                {loading ? 'Checking...' : 'Login'}
              </button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setMode('register')}
                  className="text-black hover:underline"
                >
                  New user? Register
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <nav className="bg-black text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-2xl font-bold">thaparMART</Link>
              <div className="hidden md:flex space-x-6">
                <Link to="/" className="hover:text-gray-300 transition-colors">Home</Link>
                <Link to="/marketplace" className="hover:text-gray-300 transition-colors">thaparMART</Link>
                <Link to="/about" className="hover:text-gray-300 transition-colors">About</Link>
                <Link to="/contact" className="hover:text-gray-300 transition-colors">Contact</Link>
                {user && <Link to="/profile" className="hover:text-gray-300 transition-colors">Profile</Link>}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {user ? (
                <div className="flex items-center space-x-4">
                  <span className="text-sm">Hi, {user.name}</span>
                  <button
                    onClick={logout}
                    className="bg-white text-black px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-white text-black px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Login / Register
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>
      
      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </>
  );
};

// Home Page
const Home = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="bg-black text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">thaparMART</h1>
          <p className="text-xl md:text-2xl mb-8">Your College Marketplace - Buy, Sell, Connect</p>
          <Link to="/marketplace" className="bg-white text-black px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-200 transition-colors">
            Browse Products
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">Why Choose thaparMART?</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-xl font-semibold mb-2">Electronics</h3>
              <p className="text-gray-600">Find the latest gadgets and electronics from fellow students</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-4xl mb-4">👕</div>
              <h3 className="text-xl font-semibold mb-2">Clothes</h3>
              <p className="text-gray-600">Trendy fashion items at student-friendly prices</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-4xl mb-4">📚</div>
              <h3 className="text-xl font-semibold mb-2">Stationery</h3>
              <p className="text-gray-600">All your academic supplies in one place</p>
            </div>
            <div className="text-center p-6 border border-gray-200 rounded-lg">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="text-xl font-semibold mb-2">Notes</h3>
              <p className="text-gray-600">Study materials and notes shared by students</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-black text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
              <h3 className="text-xl font-semibold mb-2">Register</h3>
              <p className="text-gray-600">Create your account with Google authentication</p>
            </div>
            <div className="text-center">
              <div className="bg-black text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
              <h3 className="text-xl font-semibold mb-2">List or Browse</h3>
              <p className="text-gray-600">Upload products to sell or browse available items</p>
            </div>
            <div className="text-center">
              <div className="bg-black text-white w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
              <h3 className="text-xl font-semibold mb-2">Connect</h3>
              <p className="text-gray-600">Contact sellers directly through their profiles</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <h3 className="text-4xl font-bold mb-2">1000+</h3>
              <p className="text-gray-600">Active Students</p>
            </div>
            <div>
              <h3 className="text-4xl font-bold mb-2">500+</h3>
              <p className="text-gray-600">Products Listed</p>
            </div>
            <div>
              <h3 className="text-4xl font-bold mb-2">200+</h3>
              <p className="text-gray-600">Successful Transactions</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-black text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Start Trading?</h2>
          <p className="text-xl mb-8">Join thousands of students already using thaparMART</p>
          <Link to="/marketplace" className="bg-white text-black px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-200 transition-colors">
            Get Started Now
          </Link>
        </div>
      </section>
    </div>
  );
};

// Marketplace Component
const Marketplace = () => {
  const { user, login } = useAuth();
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showSellForm, setShowSellForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const categories = ['Electronics', 'Clothes', 'Stationery', 'Notes'];

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products?category=${selectedCategory}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  const handleBuyClick = (product) => {
    if (!user) {
      alert("Please login to buy products!");
      login();
      return;
    }
    setSelectedProduct(product);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">thaparMART</h1>
            <p className="text-gray-600">Discover amazing products from your fellow students</p>
          </div>
          
          <div className="flex space-x-4">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            
            {user && (
              <button
                onClick={() => setShowSellForm(true)}
                className="bg-black text-white px-6 py-2 rounded-lg hover:bg-gray-800 transition-colors"
              >
                Sell Product
              </button>
            )}
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map(product => (
            <ProductCard key={product.id} product={product} onBuy={handleBuyClick} />
          ))}
        </div>

        {products.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 text-xl">No products found in this category</p>
          </div>
        )}
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal 
          product={selectedProduct} 
          onClose={() => setSelectedProduct(null)} 
        />
      )}

      {/* Sell Product Modal */}
      {showSellForm && (
        <SellProductModal 
          onClose={() => setShowSellForm(false)}
          onSuccess={() => {
            setShowSellForm(false);
            fetchProducts();
          }}
        />
      )}
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product, onBuy }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      {product.images.length > 0 && (
        <img 
          src={product.images[0]} 
          alt={product.title}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2">{product.title}</h3>
        <p className="text-gray-600 text-sm mb-2 line-clamp-2">{product.description}</p>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-2xl font-bold">₹{product.price}</p>
            <p className="text-sm text-gray-500">{product.category}</p>
          </div>
          <button
            onClick={() => onBuy(product)}
            className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

// Product Detail Modal
const ProductDetailModal = ({ product, onClose }) => {
  const navigate = useNavigate();

  const handleContactSeller = () => {
    onClose();
    navigate(`/profile/${product.seller_id}`);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">{product.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          {/* Image Gallery */}
          {product.images.length > 0 && (
            <div className="mb-4">
              <div className="grid grid-cols-1 gap-2">
                {product.images.map((image, index) => (
                  <img 
                    key={index}
                    src={image} 
                    alt={`${product.title} ${index + 1}`}
                    className="w-full h-64 object-cover rounded-lg"
                  />
                ))}
              </div>
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <p className="text-3xl font-bold">₹{product.price}</p>
              <p className="text-gray-600">{product.category}</p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Description</h3>
              <p className="text-gray-700">{product.description}</p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-2">Seller Information</h3>
              <p className="text-gray-700">Name: {product.seller_name}</p>
              <p className="text-gray-700">Email: {product.seller_email}</p>
              {product.seller_phone && (
                <p className="text-gray-700">Phone: {product.seller_phone}</p>
              )}
            </div>
            
            <button
              onClick={handleContactSeller}
              className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
            >
              Contact Seller
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Sell Product Modal with Payment Integration
const SellProductModal = ({ onClose, onSuccess }) => {
  const Razorpay = useRazorpay();
  const [step, setStep] = useState('payment'); // 'payment' or 'form'
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [hasValidToken, setHasValidToken] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    category: 'Electronics'
  });
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if user has valid payment token on mount
  useEffect(() => {
    checkPaymentTokens();
  }, []);

  const checkPaymentTokens = async () => {
    try {
      const response = await axios.get(`${API}/payment/tokens`, {
        withCredentials: true
      });
      if (response.data.length > 0) {
        setHasValidToken(true);
        setStep('form');
      }
    } catch (error) {
      console.error('Error checking payment tokens:', error);
      setHasValidToken(false);
    }
  };

  const handlePayment = async () => {
    setPaymentLoading(true);
    setError('');

    // Debug Razorpay availability
    console.log('Razorpay from hook:', Razorpay);
    console.log('Type of Razorpay:', typeof Razorpay);
    
    if (!Razorpay) {
      setError('Razorpay is not available. Please refresh the page and try again.');
      setPaymentLoading(false);
      return;
    }

    // Check profile completeness before attempting payment
    try {
      const profileResponse = await axios.get(`${API}/users/profile/complete`, {
        withCredentials: true
      });
      
      if (!profileResponse.data.complete) {
        setError('Please complete your profile with phone number first before making payment.');
        setPaymentLoading(false);
        return;
      }
      
      console.log('✅ Profile is complete, proceeding with payment');
    } catch (profileError) {
      console.error('Profile check error:', profileError);
      if (profileError.response?.status === 401) {
        setError('Please login again to continue.');
      } else {
        setError('Unable to verify profile. Please refresh and try again.');
      }
      setPaymentLoading(false);
      return;
    }

    try {
      // Create Razorpay order
      const orderResponse = await axios.post(`${API}/payment/create-order`, {}, {
        withCredentials: true
      });

      const options = {
        key: orderResponse.data.key,
        amount: orderResponse.data.amount,
        currency: orderResponse.data.currency,
        order_id: orderResponse.data.order_id,
        name: "thaparMART",
        description: "Product Upload Fee",
        image: "/logo192.png",
        handler: async (response) => {
          try {
            // Verify payment
            await axios.post(`${API}/payment/verify`, {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature
            }, {
              withCredentials: true
            });

            setHasValidToken(true);
            setStep('form');
            setError('');
          } catch (error) {
            console.error('Payment verification failed:', error);
            setError('Payment verification failed. Please try again.');
          }
        },
        prefill: {
          name: "Student",
          email: "student@thapar.edu",
          contact: "9000000000"
        },
        theme: {
          color: "#000000"
        }
      };

      console.log('Creating Razorpay instance with options:', options);
      const razorpayInstance = new Razorpay(options);
      razorpayInstance.open();
      
    } catch (error) {
      console.error('Error creating payment order:', error);
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('phone')) {
        setError('Please complete your profile with phone number first.');
      } else if (error.response?.status === 401) {
        setError('Session expired. Please login again and try.');
      } else if (error.response?.status === 500) {
        setError('Server error occurred. Please check your Razorpay account status and try again.');
      } else if (error.response?.data?.detail) {
        setError(`Error: ${error.response.data.detail}`);
      } else {
        setError('Failed to create payment order. Please try again.');
      }
    } finally {
      setPaymentLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('price', formData.price);
      formDataToSend.append('category', formData.category);
      
      images.forEach(image => {
        formDataToSend.append('images', image);
      });

      await axios.post(`${API}/products`, formDataToSend, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      onSuccess();
    } catch (error) {
      console.error('Error creating product:', error);
      if (error.response?.status === 402) {
        setError('Payment required. Please pay ₹20 to upload products.');
        setStep('payment');
        setHasValidToken(false);
      } else if (error.response?.status === 400 && error.response?.data?.detail?.includes('phone')) {
        setError('Please complete your profile with phone number before creating products.');
      } else {
        setError('Failed to create product. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">
              {step === 'payment' ? 'Payment Required' : 'Sell Product'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
              {error.includes('profile') && (
                <div className="mt-2">
                  <a 
                    href="/profile" 
                    className="text-blue-600 underline hover:text-blue-800"
                    onClick={onClose}
                  >
                    → Go to Profile to add phone number
                  </a>
                </div>
              )}
            </div>
          )}

          {step === 'payment' && (
            <div className="text-center">
              <div className="mb-6">
                <div className="text-6xl mb-4">💳</div>
                <h3 className="text-xl font-semibold mb-2">Upload Fee Required</h3>
                <p className="text-gray-600 mb-4">
                  To upload products on thaparMART, you need to pay a one-time fee of ₹20. 
                  This helps us maintain the platform and ensure quality listings.
                </p>
                <div className="bg-gray-50 p-4 rounded-lg mb-4">
                  <p className="text-2xl font-bold text-green-600">₹20</p>
                  <p className="text-sm text-gray-600">One-time payment for product uploads</p>
                </div>
              </div>
              
              <button
                onClick={handlePayment}
                disabled={paymentLoading}
                className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:bg-gray-400"
              >
                {paymentLoading ? 'Processing...' : 'Pay ₹20 & Continue'}
              </button>
              
              <p className="text-xs text-gray-500 mt-3">
                Secure payment powered by Razorpay. Supports UPI, Cards, and Net Banking.
              </p>
            </div>
          )}

          {step === 'form' && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                ✅ Payment verified! You can now upload your product.
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Product Title</label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({...formData, category: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                >
                  <option value="Electronics">Electronics</option>
                  <option value="Clothes">Clothes</option>
                  <option value="Stationery">Stationery</option>
                  <option value="Notes">Notes</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Price (₹)</label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({...formData, price: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  required
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Product Images (Multiple allowed)</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => setImages(Array.from(e.target.files))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
                <p className="text-sm text-gray-500 mt-1">You can upload multiple images. Max 10MB per image.</p>
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:bg-gray-400"
              >
                {loading ? 'Creating...' : 'Create Product'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

// Profile Component
const Profile = () => {
  const { user, checkAuth } = useAuth();
  const { pathname } = useLocation();
  const userId = pathname.split('/')[2]; // Extract userId from path like /profile/123
  const [profileUser, setProfileUser] = useState(null);
  const [userProducts, setUserProducts] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    phone: '',
    bio: ''
  });
  const [showProfileIncomplete, setShowProfileIncomplete] = useState(false);

  const isOwnProfile = !userId || userId === user?.id;
  const targetUserId = userId || user?.id;

  useEffect(() => {
    if (targetUserId) {
      fetchUserProfile();
      fetchUserProducts();
    }
  }, [targetUserId]);

  useEffect(() => {
    if (user && isOwnProfile) {
      setFormData({
        phone: user.phone || '',
        bio: user.bio || ''
      });
      // Check if profile is incomplete
      if (!user.phone || user.phone.trim() === '') {
        setShowProfileIncomplete(true);
      }
    }
  }, [user, isOwnProfile]);

  const fetchUserProfile = async () => {
    try {
      if (isOwnProfile && user) {
        setProfileUser(user);
      } else {
        const response = await axios.get(`${API}/users/${targetUserId}`);
        setProfileUser(response.data);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchUserProducts = async () => {
    try {
      const response = await axios.get(`${API}/products/user/${targetUserId}`);
      setUserProducts(response.data);
    } catch (error) {
      console.error('Error fetching user products:', error);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    
    // Validate phone number is provided
    if (!formData.phone || formData.phone.trim() === '') {
      alert('Phone number is required to complete your profile.');
      return;
    }
    
    try {
      await axios.put(`${API}/users/profile`, formData, {
        withCredentials: true
      });
      await checkAuth();
      setIsEditing(false);
      setShowProfileIncomplete(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile');
    }
  };

  if (!profileUser) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Profile Incomplete Warning */}
        {showProfileIncomplete && isOwnProfile && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
            <div className="flex justify-between items-center">
              <div>
                <strong>Complete your profile!</strong> Add your phone number to start selling products.
              </div>
              <button
                onClick={() => setIsEditing(true)}
                className="bg-yellow-600 text-white px-3 py-1 rounded text-sm hover:bg-yellow-700"
              >
                Complete Now
              </button>
            </div>
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-start space-x-6">
            {profileUser.picture && (
              <img
                src={profileUser.picture}
                alt={profileUser.name}
                className="w-24 h-24 rounded-full object-cover"
              />
            )}
            
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold mb-2">{profileUser.name}</h1>
                  <p className="text-gray-600 mb-2">{profileUser.email}</p>
                  {profileUser.phone && profileUser.phone.trim() !== '' ? (
                    <p className="text-gray-600 mb-2">📞 {profileUser.phone}</p>
                  ) : isOwnProfile && (
                    <p className="text-red-600 mb-2">📞 Phone number required</p>
                  )}
                  {profileUser.bio && (
                    <p className="text-gray-700 mb-4">{profileUser.bio}</p>
                  )}
                </div>
                
                {isOwnProfile && (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    Edit Profile
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* User's Products */}
        <div>
          <h2 className="text-2xl font-bold mb-6">
            {isOwnProfile ? 'My Products' : `${profileUser.name}'s Products`}
          </h2>
          
          {userProducts.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {userProducts.map(product => (
                <ProductCard key={product.id} product={product} onBuy={() => {}} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 text-xl">
                {isOwnProfile ? 'You haven\'t listed any products yet' : 'No products listed'}
              </p>
              {isOwnProfile && (
                <p className="text-gray-500 mt-2">
                  Complete your profile and start selling!
                </p>
              )}
            </div>
          )}
        </div>

        {/* Edit Profile Modal */}
        {isEditing && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold">Edit Profile</h2>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="text-gray-500 hover:text-gray-700 text-2xl"
                  >
                    ×
                  </button>
                </div>
                
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Phone Number <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                      placeholder="Enter your phone number"
                    />
                    <p className="text-sm text-gray-500 mt-1">Required to sell products and for buyers to contact you.</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1">Bio</label>
                    <textarea
                      rows="3"
                      value={formData.bio}
                      onChange={(e) => setFormData({...formData, bio: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-black focus:border-transparent"
                      placeholder="Tell us about yourself"
                    />
                  </div>
                  
                  <button
                    type="submit"
                    className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
                  >
                    Update Profile
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// About Page
const About = () => {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8 text-center">About thaparMART</h1>
        
        <div className="prose prose-lg mx-auto">
          <p className="text-xl text-gray-600 mb-8 text-center">
            Connecting students through a trusted marketplace for buying and selling
          </p>
          
          <div className="bg-gray-50 p-8 rounded-lg mb-8">
            <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
            <p className="text-gray-700">
              thaparMART is designed specifically for college students to create a safe, 
              convenient, and affordable marketplace. We believe in building a community 
              where students can easily buy and sell items they need for their academic journey.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-xl font-bold mb-3">What We Offer</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Electronics and gadgets</li>
                <li>• Fashion and clothing</li>
                <li>• Academic materials and stationery</li>
                <li>• Study notes and resources</li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-xl font-bold mb-3">Why Students Love Us</h3>
              <ul className="space-y-2 text-gray-700">
                <li>• Affordable student pricing</li>
                <li>• Secure Google authentication</li>
                <li>• Direct contact with sellers</li>
                <li>• Easy-to-use interface</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Contact Page
const Contact = () => {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8 text-center">Contact Us</h1>
        
        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-2xl font-bold mb-6">Get in Touch</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Email</h3>
                <p className="text-gray-700">support@thaparmart.com</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Phone</h3>
                <p className="text-gray-700">+91 12345 67890</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Address</h3>
                <p className="text-gray-700">
                  Thapar Institute of Engineering & Technology<br/>
                  Patiala, Punjab, India
                </p>
              </div>
            </div>
          </div>
          
          <div>
            <h2 className="text-2xl font-bold mb-6">Quick Help</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">How to Sell?</h3>
                <p className="text-gray-700">Login, click "Sell Product" and fill in the details</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">How to Buy?</h3>
                <p className="text-gray-700">Browse products, click on items you like, and contact the seller</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Safety Tips</h3>
                <p className="text-gray-700">Always meet in public places and verify products before purchasing</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/:userId" element={<Profile />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;