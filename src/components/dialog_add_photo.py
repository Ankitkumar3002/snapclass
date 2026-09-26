import streamlit as st
from PIL import Image, UnidentifiedImageError
from io import BytesIO


def _load_image_from_upload(uploaded_file):
    if uploaded_file is None:
        return None

    try:
        data = uploaded_file.getvalue() if hasattr(uploaded_file, 'getvalue') else uploaded_file.read()
    except Exception:
        return None

    if not data:
        return None

    try:
        image = Image.open(BytesIO(data))
        return image.copy()
    except UnidentifiedImageError:
        st.error('Please upload a valid image file.')
        return None


@st.dialog("Capture or upload photos")
def add_photos_dialog():

    st.write('Add classroom photos to scan for attendance')

    st.session_state.setdefault('attendance_images', [])

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('Camera', type=type_camera, width='stretch'):
            st.session_state.photo_tab = 'camera'



    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('Upload photos', type=type_upload, width='stretch'):
            st.session_state.photo_tab = 'upload'

    if st.session_state.photo_tab == 'camera':
        st.caption('Camera access can be flaky in some browsers. If it does not open, switch to Upload photos.')
        cam_photo = st.camera_input('Take Snapshot', key='dialog_cam')
        if cam_photo is not None:
            image = _load_image_from_upload(cam_photo)
            if image is not None:
                st.session_state.attendance_images.append(image)
                st.toast('Photo Captured')


    if st.session_state.photo_tab == 'upload':
        uploaded_files = st.file_uploader('choose image files', type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key='dialog_upload')

        if uploaded_files:
            added_count = 0
            for uploaded_file in uploaded_files:
                image = _load_image_from_upload(uploaded_file)
                if image is not None:
                    st.session_state.attendance_images.append(image)
                    added_count += 1

            if added_count:
                st.toast('Photo Uploaded Successfully')

    st.divider()
    if st.button('Done', type='primary', width='stretch'):
        st.session_state.photo_tab = 'camera'