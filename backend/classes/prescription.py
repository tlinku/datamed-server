from flask import current_app
from datetime import datetime

class Prescription_Methods:
    @staticmethod
    def DeleteByName(user_id, first_name, last_name):
        conn = None
        cur = None

        try:
            conn = current_app.db_pool.getconn()
            cur = conn.cursor()
            
            cur.execute("""
                DELETE FROM prescriptions 
                WHERE user_id = %s 
                AND first_name = %s 
                AND last_name = %s
                RETURNING id
            """, (user_id, first_name, last_name))
            
            deleted = cur.fetchall()
            conn.commit()
            if not deleted:
                return False, "No matching prescriptions found"
                
            return True, f"Successfully deleted {len(deleted)} prescription(s)"
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error deleting prescriptions: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                current_app.db_pool.putconn(conn)

    @staticmethod
    def findPrescriptionsByPerson(user_id, first_name, last_name, start_date = None, end_date = None):
        conn = None
        cur = None
        
        try:
            conn = current_app.db_pool.getconn()
            cur = conn.cursor()
            
            query = """
                SELECT id, first_name, last_name, pesel, 
                    issue_date, expiry_date, pdf_url, med_info_for_search
                FROM prescriptions 
                WHERE user_id = %s 
                AND first_name = %s 
                AND last_name = %s
            """
            params = [user_id, first_name, last_name]
            
            if start_date:
                query += " AND issue_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND issue_date <= %s"
                params.append(end_date)
                
            query += " ORDER BY issue_date DESC"
            
            cur.execute(query, tuple(params))
            prescriptions = cur.fetchall()
            
            if not prescriptions:
                return False, "No matching prescriptions found"
                
            result = [{
                'id': p[0],
                'first_name': p[1],
                'last_name': p[2],
                'pesel': p[3],
                'issue_date': p[4].strftime('%Y-%m-%d'),
                'expiry_date': p[5].strftime('%Y-%m-%d'),
                'pdf_url': p[6],
                'med_info': p[7]
            } for p in prescriptions]
            
            return True, result
            
        except Exception as e:
            return False, f"Error finding prescriptions: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                current_app.db_pool.putconn(conn)

    @staticmethod
    def findByMedication(user_id, med_pattern):
        conn = None
        cur = None
        try:
            conn = current_app.db_pool.getconn()
            cur = conn.cursor()
            
            query = """
                SELECT id, first_name, last_name, pesel, 
                    issue_date, expiry_date, pdf_url, med_info_for_search
                FROM prescriptions 
                WHERE user_id = %s 
                AND med_info_for_search ILIKE %s
                ORDER BY issue_date DESC
            """
            search_pattern = f'%{med_pattern}%'
            
            cur.execute(query, (user_id, search_pattern))
            prescriptions = cur.fetchall()
            
            if not prescriptions:
                return False, "No prescriptions found with this medication"
                
            result = [{
                'id': p[0],
                'first_name': p[1],
                'last_name': p[2],
                'pesel': p[3],
                'issue_date': p[4].strftime('%Y-%m-%d'),
                'expiry_date': p[5].strftime('%Y-%m-%d'),
                'pdf_url': p[6],
                'med_info': p[7]
            } for p in prescriptions]
            
            return True, result
            
        except Exception as e:
            return False, f"Error searching prescriptions: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                current_app.db_pool.putconn(conn)

    @staticmethod
    def deletePrescriptionsByDate(user_id: int, before_date: str = None):
        conn = None
        cur = None
        
        try:
            conn = current_app.db_pool.getconn()
            cur = conn.cursor()
            
            if not before_date:
                before_date = datetime.now().strftime('%Y-%m-%d')
                
            query = """
                DELETE FROM prescriptions 
                WHERE user_id = %s 
                AND expiry_date < %s
                RETURNING id
            """
            
            cur.execute(query, (user_id, before_date))
            deleted = cur.fetchall()
            conn.commit()
            
            if not deleted:
                return False, "No expired prescriptions found"
                
            return True, f"Successfully deleted {len(deleted)} expired prescription(s)"
            
        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error deleting expired prescriptions: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                current_app.db_pool.putconn(conn)
    
    @staticmethod
    def findAllPrescriptions(user_id: int):
        conn = None
        cur = None
        try:
            conn = current_app.db_pool.getconn()
            cur = conn.cursor()
            
            query = """
                SELECT id, first_name, last_name, pesel, 
                    issue_date, expiry_date, pdf_url, med_info_for_search
                FROM prescriptions 
                WHERE user_id = %s
                ORDER BY issue_date DESC
            """
            
            cur.execute(query, (user_id,))
            prescriptions = cur.fetchall()
            
            if not prescriptions:
                return False, "No prescriptions found for this user"
                
            result = [{
                'id': p[0],
                'first_name': p[1],
                'last_name': p[2],
                'pesel': p[3],
                'issue_date': p[4].strftime('%Y-%m-%d'),
                'expiry_date': p[5].strftime('%Y-%m-%d'),
                'pdf_url': p[6],
                'med_info': p[7]
            } for p in prescriptions]
            
            return True, result
            
        except Exception as e:
            return False, f"Error fetching prescriptions: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                current_app.db_pool.putconn(conn)