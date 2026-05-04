from supabase import create_client, Client
from config import Config
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SupabaseDB:
    """Supabase database handler"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.init_supabase()
    
    def init_supabase(self):
        """Initialize Supabase connection"""
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            self.supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            self.create_tables()
    
    def create_tables(self):
        """Create necessary tables in Supabase if they don't exist"""
        # Note: You need to create these tables manually in Supabase SQL editor
        # Run the SQL script below in Supabase SQL editor
        
        tables_sql = """
        -- Create bookings table
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            email_address VARCHAR(100) NOT NULL,
            country VARCHAR(50) NOT NULL,
            duration_stay INTEGER NOT NULL,
            check_in_date DATE NOT NULL,
            number_persons INTEGER NOT NULL,
            special_requests TEXT,
            selected_room JSONB NOT NULL,
            total_price DECIMAL(15, 2) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            booking_reference VARCHAR(20) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create admin_users table
        CREATE TABLE IF NOT EXISTS admin_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(email_address);
        CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
        CREATE INDEX IF NOT EXISTS idx_bookings_check_in ON bookings(check_in_date);
        CREATE INDEX IF NOT EXISTS idx_bookings_reference ON bookings(booking_reference);
        
        -- Insert default admin (password: admin123)
        -- Password hash will be created during first run
        """
        
        # You need to run this SQL manually in Supabase SQL editor
    
    def create_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking in Supabase"""
        try:
            # Generate unique booking reference
            import random
            import string
            booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            booking_data = {
                'full_name': data['full_name'],
                'phone_number': data['phone_number'],
                'email_address': data['email_address'],
                'country': data['country'],
                'duration_stay': data['duration_stay'],
                'check_in_date': data['check_in_date'],
                'number_persons': data['number_persons'],
                'special_requests': data.get('special_requests', ''),
                'selected_room': json.dumps(data['selected_room']),
                'total_price': data['total_price'],
                'booking_reference': booking_ref,
                'status': 'pending'
            }
            
            result = self.supabase.table('bookings').insert(booking_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'booking_id': result.data[0]['id'],
                    'booking_reference': booking_ref,
                    'data': result.data[0]
                }
            else:
                return {'success': False, 'error': 'Failed to create booking'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_booking(self, booking_id: int) -> Optional[Dict]:
        """Get a booking by ID"""
        try:
            result = self.supabase.table('bookings').select('*').eq('id', booking_id).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception:
            return None
    
    def update_booking_status(self, booking_id: int, status: str) -> bool:
        """Update booking status"""
        try:
            result = self.supabase.table('bookings').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', booking_id).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    def get_all_bookings(self, limit: int = 100, offset: int = 0) -> list:
        """Get all bookings with pagination"""
        try:
            result = self.supabase.table('bookings')\
                .select('*')\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            return result.data if result.data else []
        except Exception:
            return []

# Initialize database instance
db = SupabaseDB()