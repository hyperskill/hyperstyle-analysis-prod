# TODO: fix the jba README
import streamlit as st


def main():
    st.header('JBA course analysis')

    submissions_path = st.text_input('Submissions path:', value=st.session_state.get('submissions_path', ''))

    course_structure_path = st.text_input(
        'Course structure path:',
        value=st.session_state.get('course_structure_path', ''),
    )

    course_name = st.text_input('Course name:', value=st.session_state.get('course_name', ''))

    if not submissions_path:
        st.info('You should enter the submissions path.')
        st.stop()

    st.session_state['submissions_path'] = submissions_path

    if not course_structure_path:
        st.info('You should enter the course structure path.')
        st.stop()

    st.session_state['course_structure_path'] = course_structure_path

    if not course_name:
        st.info('You should enter the course name.')
        st.stop()

    st.session_state['course_name'] = course_name

    # TODO: write README


if __name__ == '__main__':
    main()
