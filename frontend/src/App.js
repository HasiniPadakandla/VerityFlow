import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { ShieldCheck, History, AlertTriangle, CheckCircle2, ClipboardPaste, Download, Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import jsPDF from "jspdf";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-8 w-8 text-blue-800" strokeWidth={2.5} />
            <span className="text-2xl font-extrabold text-slate-900" style={{fontFamily: 'Manrope, sans-serif'}}>Verityflow</span>
          </div>
          <div className="flex gap-2">
            <Link to="/">
              <Button 
                variant={location.pathname === "/" ? "default" : "ghost"}
                className={location.pathname === "/" ? "bg-blue-800 hover:bg-blue-900 text-white" : "text-slate-600 hover:text-blue-800 hover:bg-blue-50"}
                data-testid="nav-analyzer-btn"
              >
                <ShieldCheck className="h-4 w-4 mr-2" />
                Analyzer
              </Button>
            </Link>
            <Link to="/history">
              <Button 
                variant={location.pathname === "/history" ? "default" : "ghost"}
                className={location.pathname === "/history" ? "bg-blue-800 hover:bg-blue-900 text-white" : "text-slate-600 hover:text-blue-800 hover:bg-blue-50"}
                data-testid="nav-history-btn"
              >
                <History className="h-4 w-4 mr-2" />
                History
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

const Home = () => {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeMessage = async () => {
    if (!message.trim()) {
      toast.error("Please enter a message to analyze");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/analyze-message`, { message });
      setResult(response.data);
      toast.success("Analysis complete!");
    } catch (error) {
      console.error("Analysis error:", error);
      toast.error("Failed to analyze message. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const pasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setMessage(text);
      toast.success("Message pasted from clipboard");
    } catch (error) {
      toast.error("Failed to read clipboard. Please paste manually.");
    }
  };

  const getVerdictColor = (verdict) => {
    const v = verdict?.toLowerCase();
    if (v === "legitimate") return { border: "border-emerald-500", bg: "bg-emerald-50", text: "text-emerald-800", badge: "bg-emerald-100 text-emerald-800 border-emerald-200" };
    if (v === "scam" || v === "phishing") return { border: "border-rose-500", bg: "bg-rose-50", text: "text-rose-800", badge: "bg-rose-100 text-rose-800 border-rose-200" };
    return { border: "border-amber-500", bg: "bg-amber-50", text: "text-amber-800", badge: "bg-amber-100 text-amber-800 border-amber-200" };
  };

  const getVerdictIcon = (verdict) => {
    const v = verdict?.toLowerCase();
    if (v === "legitimate") return <CheckCircle2 className="h-8 w-8" />;
    return <AlertTriangle className="h-8 w-8" />;
  };

  const colors = result ? getVerdictColor(result.verdict) : null;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 tracking-tight mb-4" style={{fontFamily: 'Manrope, sans-serif'}}>
            Detect Scams, Fake News & Phishing
          </h1>
          <p className="text-base md:text-lg text-slate-600 max-w-2xl mx-auto" style={{fontFamily: 'Public Sans, sans-serif'}}>
            Paste any suspicious WhatsApp message and get instant AI-powered analysis with clear, actionable insights.
          </p>
        </div>

        <Card className="rounded-xl border border-slate-200 bg-white shadow-sm mb-8 card-hover">
          <CardHeader>
            <CardTitle className="text-2xl font-semibold" style={{fontFamily: 'Manrope, sans-serif'}}>Analyze Message</CardTitle>
            <CardDescription>Paste a forwarded message to check if it's legitimate or suspicious</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Paste your WhatsApp message here..."
                className="min-h-[200px] rounded-xl border-slate-200 bg-white p-6 text-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none shadow-inner"
                data-testid="message-input"
              />
            </div>
            <div className="flex gap-3">
              <Button
                onClick={analyzeMessage}
                disabled={loading}
                className="flex-1 bg-blue-800 hover:bg-blue-900 text-white rounded-lg px-8 py-6 text-lg font-semibold shadow-lg shadow-blue-900/20 analyze-btn"
                data-testid="analyze-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="h-5 w-5 mr-2" />
                    Analyze Message
                  </>
                )}
              </Button>
              <Button
                onClick={pasteFromClipboard}
                variant="outline"
                className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg px-6 py-6 font-medium"
                data-testid="paste-btn"
              >
                <ClipboardPaste className="h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {result && (
          <div className="verdict-card" data-testid="result-card">
            <Card className={`rounded-2xl ${colors.border} border-l-8 shadow-lg bg-white p-8`}>
              <div className="space-y-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`${colors.text}`}>
                      {getVerdictIcon(result.verdict)}
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-900" style={{fontFamily: 'Manrope, sans-serif'}} data-testid="verdict-text">
                        {result.verdict}
                      </h2>
                      <p className="text-sm text-slate-600 mt-1">Analysis completed</p>
                    </div>
                  </div>
                  <Badge className={`${colors.badge} inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold border`} data-testid="confidence-badge">
                    {(result.confidence * 100).toFixed(0)}% Confidence
                  </Badge>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <Card className="p-6 rounded-xl bg-slate-50 border border-slate-100 shadow-sm">
                    <h3 className="text-lg font-semibold text-slate-900 mb-3" style={{fontFamily: 'Manrope, sans-serif'}}>Key Findings</h3>
                    <ul className="space-y-2">
                      {result.reasons && result.reasons.length > 0 ? (
                        result.reasons.map((reason, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                            <span className="text-blue-800 mt-0.5">•</span>
                            <span>{reason}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-sm text-slate-600">No specific reasons detected</li>
                      )}
                    </ul>
                  </Card>

                  <Card className="p-6 rounded-xl bg-slate-50 border border-slate-100 shadow-sm">
                    <h3 className="text-lg font-semibold text-slate-900 mb-3" style={{fontFamily: 'Manrope, sans-serif'}}>Safety Advice</h3>
                    <p className="text-sm text-slate-700 leading-relaxed">{result.safety_advice}</p>
                  </Card>
                </div>

                {result.red_flags && result.red_flags.length > 0 && (
                  <Card className="p-6 rounded-xl bg-rose-50 border border-rose-100">
                    <h3 className="text-lg font-semibold text-rose-900 mb-3" style={{fontFamily: 'Manrope, sans-serif'}}>Red Flags Detected</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.red_flags.map((flag, idx) => (
                        <Badge key={idx} variant="outline" className="bg-white text-rose-700 border-rose-200 text-xs">
                          {flag}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                )}

                {result.suspicious_urls && result.suspicious_urls.length > 0 && (
                  <Card className="p-6 rounded-xl bg-amber-50 border border-amber-100">
                    <h3 className="text-lg font-semibold text-amber-900 mb-3" style={{fontFamily: 'Manrope, sans-serif'}}>Suspicious URLs</h3>
                    <ul className="space-y-1">
                      {result.suspicious_urls.map((url, idx) => (
                        <li key={idx} className="text-xs font-mono text-amber-800 bg-white px-3 py-2 rounded border border-amber-200">
                          {url}
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

                {result.explanation && (
                  <Card className="p-6 rounded-xl bg-blue-50 border border-blue-100">
                    <h3 className="text-lg font-semibold text-blue-900 mb-3" style={{fontFamily: 'Manrope, sans-serif'}}>Detailed Explanation</h3>
                    <p className="text-sm text-blue-800 leading-relaxed">{result.explanation}</p>
                  </Card>
                )}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchHistory = async (searchTerm = "") => {
    setLoading(true);
    try {
      const params = searchTerm ? `?search=${encodeURIComponent(searchTerm)}` : "";
      const response = await axios.get(`${API}/history${params}`);
      setHistory(response.data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
      toast.error("Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  useState(() => {
    fetchHistory();
  }, []);

  const handleSearch = () => {
    fetchHistory(search);
  };

  const exportToPDF = async () => {
    try {
      const doc = new jsPDF();
      doc.setFontSize(20);
      doc.text("Verityflow Analysis History", 14, 20);
      
      let y = 35;
      doc.setFontSize(10);
      
      history.slice(0, 20).forEach((item, index) => {
        if (y > 270) {
          doc.addPage();
          y = 20;
        }
        
        doc.setFont("helvetica", "bold");
        doc.text(`${index + 1}. ${item.verdict} (${(item.confidence * 100).toFixed(0)}%)`, 14, y);
        y += 6;
        
        doc.setFont("helvetica", "normal");
        const message = item.message.substring(0, 100) + (item.message.length > 100 ? "..." : "");
        const lines = doc.splitTextToSize(message, 180);
        doc.text(lines, 14, y);
        y += lines.length * 5 + 8;
      });
      
      doc.save("verityflow-history.pdf");
      toast.success("PDF exported successfully!");
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Failed to export PDF");
    }
  };

  const exportToCSV = async () => {
    try {
      const response = await axios.get(`${API}/export?format=csv`);
      const blob = new Blob([response.data.data], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "verityflow-history.csv";
      a.click();
      toast.success("CSV exported successfully!");
    } catch (error) {
      console.error("Export error:", error);
      toast.error("Failed to export CSV");
    }
  };

  const getVerdictBadge = (verdict) => {
    const v = verdict?.toLowerCase();
    if (v === "legitimate") return "bg-emerald-100 text-emerald-800 border-emerald-200";
    if (v === "scam" || v === "phishing") return "bg-rose-100 text-rose-800 border-rose-200";
    return "bg-amber-100 text-amber-800 border-amber-200";
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-4" style={{fontFamily: 'Manrope, sans-serif'}}>
            Analysis History
          </h1>
          <p className="text-base text-slate-600" style={{fontFamily: 'Public Sans, sans-serif'}}>
            View and export your past message analyses
          </p>
        </div>

        <Card className="rounded-xl border border-slate-200 bg-white shadow-sm mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 flex gap-2">
                <Input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search messages..."
                  className="h-12 rounded-lg border-slate-200 bg-slate-50 px-4 focus:bg-white transition-colors"
                  data-testid="search-input"
                />
                <Button
                  onClick={handleSearch}
                  className="bg-blue-800 hover:bg-blue-900 text-white rounded-lg px-6"
                  data-testid="search-btn"
                >
                  <Search className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={exportToPDF}
                  variant="outline"
                  className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg px-4"
                  data-testid="export-pdf-btn"
                >
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </Button>
                <Button
                  onClick={exportToCSV}
                  variant="outline"
                  className="bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg px-4"
                  data-testid="export-csv-btn"
                >
                  <Download className="h-4 w-4 mr-2" />
                  CSV
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className="text-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-800 mx-auto" />
            <p className="text-slate-600 mt-4">Loading history...</p>
          </div>
        ) : history.length === 0 ? (
          <Card className="rounded-xl border border-slate-200 bg-white shadow-sm p-12 text-center">
            <History className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2" style={{fontFamily: 'Manrope, sans-serif'}}>No History Yet</h3>
            <p className="text-slate-600">Analyze your first message to see it here</p>
          </Card>
        ) : (
          <div className="space-y-3">
            {history.map((item) => (
              <Card key={item.id} className="rounded-xl border border-slate-200 bg-white shadow-sm history-item" data-testid="history-item">
                <CardContent className="p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge className={`${getVerdictBadge(item.verdict)} inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border`}>
                          {item.verdict}
                        </Badge>
                        <span className="text-xs text-slate-500 font-mono" style={{fontFamily: 'JetBrains Mono, monospace'}}>
                          {(item.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                      <p className="text-sm text-slate-700 line-clamp-2">{item.message}</p>
                    </div>
                    <div className="text-xs text-slate-500 whitespace-nowrap">
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" />
    </div>
  );
}

export default App;
