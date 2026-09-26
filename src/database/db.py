import streamlit as st
from src.database.config import supabase
import bcrypt


@st.cache_data(show_spinner=False, ttl=30)
def get_cached_query(table_name, query, params=None):
    return None


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())


def _safe_supabase_execute(operation, default=None):
    if supabase is None:
        return default
    try:
        return operation()
    except Exception:
        return default


def clear_db_cache():
    st.cache_data.clear()


def check_teacher_exists(username):
    response = _safe_supabase_execute(
        lambda: supabase.table("teachers").select("username").eq("username", username).execute(),
        default=None,
    )
    return bool(getattr(response, "data", None)) if response is not None else False



def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}
    response = _safe_supabase_execute(
        lambda: supabase.table("teachers").insert(data).execute(),
        default=None,
    )
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None


def teacher_login(username, password):
    response = _safe_supabase_execute(
        lambda: supabase.table("teachers").select("*").eq("username", username).execute(),
        default="ERROR"
    )
    if response == "ERROR":
        return False, "Unable to reach the database. Please check your connection."
    
    data = getattr(response, "data", None) if response is not None else None
    if data:
        teacher = data[0]
        if check_pass(password, teacher['password']):
            return True, teacher
    return False, "Invalid username and password combo"


def get_all_students():
    response = _safe_supabase_execute(lambda: supabase.table('students').select("*").execute(), default=None)
    return getattr(response, "data", None) if response is not None else []

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding':face_embedding, "voice_embedding": voice_embedding}
    response = _safe_supabase_execute(lambda: supabase.table('students').insert(data).execute(), default=None)
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None


def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = _safe_supabase_execute(lambda: supabase.table("subjects").insert(data).execute(), default=None)
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None

@st.cache_data(show_spinner=False, ttl=30)
def get_teacher_subjects(teacher_id):
    response = _safe_supabase_execute(
        lambda: supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute(),
        default=None,
    )
    subjects = getattr(response, "data", None) if response is not None else []


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects


def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response = _safe_supabase_execute(lambda: supabase.table('subject_students').insert(data).execute(), default=None)
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None


def  unenroll_student_to_subject(student_id, subject_id):
    response = _safe_supabase_execute(lambda: supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute(), default=None)
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None



@st.cache_data(show_spinner=False, ttl=30)
def get_student_subjects(student_id):
    response = _safe_supabase_execute(lambda: supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute(), default=None)
    return getattr(response, "data", None) if response is not None else []


@st.cache_data(show_spinner=False, ttl=30)
def get_student_attendance(student_id):
    response = _safe_supabase_execute(lambda: supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute(), default=None)
    return getattr(response, "data", None) if response is not None else []


def create_attendance(logs):
    response = _safe_supabase_execute(lambda: supabase.table('attendance_logs').insert(logs).execute(), default=None)
    clear_db_cache()
    return getattr(response, "data", None) if response is not None else None

@st.cache_data(show_spinner=False, ttl=30)
def get_attendance_for_teacher(teacher_id):
    response = _safe_supabase_execute(lambda: supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute(), default=None)
    return getattr(response, "data", None) if response is not None else []