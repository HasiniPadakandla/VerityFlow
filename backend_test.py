import requests
import sys
import json
from datetime import datetime

class VerityflowAPITester:
    def __init__(self, base_url="https://truthscan-57.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("Root API Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Root API Endpoint", False, f"Error: {str(e)}")
            return False

    def test_analyze_scam_message(self):
        """Test analyze endpoint with scam message"""
        scam_message = "CONGRATULATIONS! You have WON $1,000,000 in our lottery! Click here to CLAIM NOW! Act immediately or lose your prize! Send your bank details to claim."
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze-message",
                json={"message": scam_message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                verdict = data.get('verdict', '').lower()
                confidence = data.get('confidence', 0)
                red_flags = data.get('red_flags', [])
                
                # Check if scam was detected correctly
                scam_detected = verdict in ['scam', 'phishing', 'suspicious']
                details += f", Verdict: {data.get('verdict')}, Confidence: {confidence:.2f}, Red Flags: {len(red_flags)}"
                
                if not scam_detected:
                    success = False
                    details += " - ISSUE: Scam not detected properly"
                    
            self.log_test("Analyze Scam Message", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Analyze Scam Message", False, f"Error: {str(e)}")
            return False, {}

    def test_analyze_legitimate_message(self):
        """Test analyze endpoint with legitimate message"""
        legitimate_message = "Hey, are we still meeting for lunch tomorrow at 1 PM? Let me know if you need to reschedule."
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze-message",
                json={"message": legitimate_message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                verdict = data.get('verdict', '').lower()
                confidence = data.get('confidence', 0)
                
                # Check if legitimate message was classified correctly
                legitimate_detected = verdict == 'legitimate'
                details += f", Verdict: {data.get('verdict')}, Confidence: {confidence:.2f}"
                
                if not legitimate_detected:
                    success = False
                    details += " - ISSUE: Legitimate message not classified correctly"
                    
            self.log_test("Analyze Legitimate Message", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Analyze Legitimate Message", False, f"Error: {str(e)}")
            return False, {}

    def test_analyze_phishing_message(self):
        """Test analyze endpoint with phishing message"""
        phishing_message = "Security Alert: Suspicious activity detected on your account. Verify your identity immediately at http://192.168.1.1/secure and enter your password, CVV and PIN to prevent account suspension."
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze-message",
                json={"message": phishing_message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                verdict = data.get('verdict', '').lower()
                confidence = data.get('confidence', 0)
                suspicious_urls = data.get('suspicious_urls', [])
                
                # Check if phishing was detected
                phishing_detected = verdict in ['phishing', 'scam', 'suspicious']
                details += f", Verdict: {data.get('verdict')}, Confidence: {confidence:.2f}, Suspicious URLs: {len(suspicious_urls)}"
                
                if not phishing_detected:
                    success = False
                    details += " - ISSUE: Phishing not detected properly"
                    
            self.log_test("Analyze Phishing Message", success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            self.log_test("Analyze Phishing Message", False, f"Error: {str(e)}")
            return False, {}

    def test_empty_message(self):
        """Test analyze endpoint with empty message"""
        try:
            response = requests.post(
                f"{self.api_url}/analyze-message",
                json={"message": ""},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 400 for empty message
            success = response.status_code == 400
            details = f"Status: {response.status_code}"
            
            if response.status_code == 400:
                details += " - Correctly rejected empty message"
            else:
                details += " - Should reject empty message with 400"
                
            self.log_test("Empty Message Validation", success, details)
            return success
            
        except Exception as e:
            self.log_test("Empty Message Validation", False, f"Error: {str(e)}")
            return False

    def test_history_endpoint(self):
        """Test history endpoint"""
        try:
            response = requests.get(f"{self.api_url}/history", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Records: {len(data)}"
                
                # Check if response is a list
                if not isinstance(data, list):
                    success = False
                    details += " - ISSUE: Response should be a list"
                    
            self.log_test("History Endpoint", success, details)
            return success, response.json() if success else []
            
        except Exception as e:
            self.log_test("History Endpoint", False, f"Error: {str(e)}")
            return False, []

    def test_history_search(self):
        """Test history endpoint with search"""
        try:
            response = requests.get(f"{self.api_url}/history?search=congratulations", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", Search Results: {len(data)}"
                
            self.log_test("History Search", success, details)
            return success
            
        except Exception as e:
            self.log_test("History Search", False, f"Error: {str(e)}")
            return False

    def test_export_csv(self):
        """Test CSV export endpoint"""
        try:
            response = requests.get(f"{self.api_url}/export?format=csv", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                csv_format = data.get('format') == 'csv'
                has_data = 'data' in data
                details += f", Format: {data.get('format')}, Has Data: {has_data}"
                
                if not (csv_format and has_data):
                    success = False
                    details += " - ISSUE: Invalid CSV export format"
                    
            self.log_test("CSV Export", success, details)
            return success
            
        except Exception as e:
            self.log_test("CSV Export", False, f"Error: {str(e)}")
            return False

    def test_export_json(self):
        """Test JSON export endpoint"""
        try:
            response = requests.get(f"{self.api_url}/export?format=json", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                json_format = data.get('format') == 'json'
                has_data = 'data' in data
                details += f", Format: {data.get('format')}, Has Data: {has_data}"
                
                if not (json_format and has_data):
                    success = False
                    details += " - ISSUE: Invalid JSON export format"
                    
            self.log_test("JSON Export", success, details)
            return success
            
        except Exception as e:
            self.log_test("JSON Export", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Verityflow Backend API Tests")
        print("=" * 50)
        
        # Test basic connectivity
        if not self.test_root_endpoint():
            print("❌ Root endpoint failed - stopping tests")
            return False
            
        # Test message analysis
        self.test_analyze_scam_message()
        self.test_analyze_legitimate_message() 
        self.test_analyze_phishing_message()
        self.test_empty_message()
        
        # Test history and export
        self.test_history_endpoint()
        self.test_history_search()
        self.test_export_csv()
        self.test_export_json()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = VerityflowAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': tester.tests_passed / tester.tests_run if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())