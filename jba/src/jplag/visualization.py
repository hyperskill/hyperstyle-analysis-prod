import itertools
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import streamlit as st

from jba.src.jplag.jplag_config import JPlagConfiguration, Algorithm, Metric, Preprocessing, InterClusterSimilarity
from jba.src.jplag.jplag_runner import JPlagRunner, create_submission_files, get_clusters
from jba.src.jplag.submissions_converter import convert_submissions
from jba.src.models.edu_columns import EduColumnName
from jba.src.visualization.common.utils import get_edu_name_columns

THRESHOLDS = list(map(lambda value: round(value, 2), np.arange(0, 1.1, 0.1)))


@st.cache_data
def generate_submissions(submissions: pd.DataFrame, output_path: Path):
    create_submission_files(submissions, output_path)


@st.cache_data
def run_jplag(task_id: int, config: JPlagConfiguration, executable_path: Path, output_path: Path):
    JPlagRunner().run(task_id, output_path, executable_path, config)


def show_common_setting(config: JPlagConfiguration) -> JPlagConfiguration:
    columns = st.columns(3)

    with columns[0]:
        algorithm = st.selectbox(
            'Algorithm:',
            options=Algorithm,
            format_func=lambda option: option.name.replace('_', ' ').capitalize(),
            index=list(Algorithm).index(Algorithm.get_default()),
        )

    with columns[1]:
        metric = st.selectbox(
            'Metric:',
            options=Metric,
            format_func=lambda option: option.name.capitalize(),
            index=list(Metric).index(Metric.get_default()),
        )

    with columns[2]:
        preprocessing = st.selectbox(
            'Preprocessing:',
            options=Preprocessing,
            format_func=lambda option: option.value,
            index=list(Preprocessing).index(Preprocessing.get_default()),
        )

    return replace(config, algorithm=algorithm, metric=metric, preprocessing=preprocessing)


def format_threshold_option(
    threshold: int,
    clusters: List[List[int]],
    separate_solutions_by_threshold: Dict[int, List[int]],
) -> str:
    clusters_tuples = tuple(tuple(sorted(cluster)) for cluster in clusters)
    clusters_tuples += tuple(sorted(separate_solutions_by_threshold[threshold]))

    return (
        f'{threshold:.2} -- {len(clusters)} JPlag clusters '
        f'({len(separate_solutions_by_threshold[threshold])} separate solutions)'
    )


def show_agglomerative_clustering(
    submissions: pd.DataFrame,
    task_id: int,
    config: JPlagConfiguration,
    executable_path: Path,
    output_path: Path,
):
    similarity = st.selectbox(
        'Similarity:',
        options=InterClusterSimilarity,
        format_func=lambda option: option.name.capitalize(),
        index=list(InterClusterSimilarity).index(InterClusterSimilarity.get_default()),
    )

    config = replace(config, inter_cluster_similarity=similarity)

    for threshold in THRESHOLDS:
        run_jplag(task_id, replace(config, threshold=threshold), executable_path, output_path)

    clusters_by_threshold = {}
    for threshold in THRESHOLDS:
        try:
            clusters_by_threshold[threshold] = get_clusters(
                task_id,
                replace(config, threshold=threshold),
                output_path,
            )
        except Exception as e:
            print(e)

    separate_solutions_by_threshold = {
        threshold: set(  # noqa: WPS441
            submissions[submissions[EduColumnName.TASK_ID.value] == task_id][EduColumnName.ID.value].unique()
        )
        - set(itertools.chain.from_iterable(cluster))
        for threshold, cluster in clusters_by_threshold.items()
    }

    left, middle, right = st.columns([2, 1, 1])

    with left:
        threshold, clusters = st.selectbox(
            'Threshold:',
            index=list(clusters_by_threshold.keys()).index(JPlagConfiguration.threshold),
            options=clusters_by_threshold.items(),
            format_func=lambda item: format_threshold_option(*item, separate_solutions_by_threshold),
        )

    separate_solutions = separate_solutions_by_threshold[threshold]  # noqa: WPS441
    all_clusters = clusters + [[solution] for solution in separate_solutions]

    with middle:
        cluster_number = st.number_input(
            'Cluster:',
            min_value=1,
            max_value=len(clusters) + len(separate_solutions),
            step=1,
        )

    cluster = all_clusters[cluster_number - 1]

    with right:
        member_number = st.number_input('Member:', min_value=1, max_value=len(cluster), step=1)

    cluster_member_id = cluster[member_number - 1]

    if cluster_number > len(clusters):
        st.info('This is a separate cluster.')

    st.write(len(cluster))

    return cluster_member_id


def show_spectral_clustering(
    submissions: pd.DataFrame,
    task_id: int,
    config: JPlagConfiguration,
    executable_path: Path,
    output_path: Path,
):
    columns = st.columns(5)

    with columns[0]:
        bandwidth = st.number_input('Bandwidth:', value=JPlagConfiguration().bandwidth)

    with columns[1]:
        noise = st.number_input('Noise:', value=JPlagConfiguration().noise)

    with columns[2]:
        min_runs = st.number_input('Min runs:', value=JPlagConfiguration().min_runs)

    with columns[3]:
        max_runs = st.number_input('Max runs:', value=JPlagConfiguration().max_runs)

    with columns[4]:
        k_means_iterations = st.number_input('K-means iterations:', value=JPlagConfiguration().k_means_iterations)

    config = replace(
        config,
        bandwidth=bandwidth,
        noise=noise,
        min_runs=min_runs,
        max_runs=max_runs,
        k_means_iterations=k_means_iterations,
    )

    run_jplag(task_id, config, executable_path, output_path)

    clusters = get_clusters(task_id, config, output_path)

    separate_solutions = set(submissions[submissions[EduColumnName.TASK_ID.value] == task_id]["id"].unique()) - set(
        itertools.chain.from_iterable(clusters)
    )

    st.write(f'{len(clusters)} JPlag clusters ({len(separate_solutions)} separate solutions)')

    all_clusters = clusters + [[solution] for solution in separate_solutions]

    left, right = st.columns(2)

    with left:
        cluster_number = st.number_input(
            'Cluster:',
            min_value=1,
            max_value=len(clusters) + len(separate_solutions),
            step=1,
        )

    cluster = all_clusters[cluster_number - 1]

    st.write(len(cluster))

    with right:
        member = st.number_input('Member:', min_value=1, max_value=len(cluster))

    cluster_member_id = cluster[member - 1]

    if cluster_number > len(clusters):
        st.info('This is a separate cluster.')

    return cluster_member_id


def main():
    submissions_path = st.text_input('Submissions:')
    course_structure_path = st.text_input('Course structure path:')
    executable_path = st.text_input('Executable path:')
    output_path = st.text_input('Output:')

    if not submissions_path or not course_structure_path or not executable_path or not output_path:
        st.stop()

    submissions_path = Path(submissions_path)
    course_structure_path = Path(course_structure_path)
    executable_path = Path(executable_path)
    output_path = Path(output_path)

    submissions = pd.read_csv(submissions_path)
    submissions = convert_submissions(submissions)

    course_structure = pd.read_csv(course_structure_path)

    generate_submissions(submissions, output_path)

    task_id = st.selectbox(
        'Task:',
        options=course_structure[EduColumnName.TASK_ID.value].unique(),
        format_func=lambda task_id: '/'.join(
            course_structure[course_structure[EduColumnName.TASK_ID.value] == task_id]
            .reset_index()
            .loc[0, get_edu_name_columns(course_structure)]
        ),
    )

    config = JPlagConfiguration()
    config = show_common_setting(config)

    match config.algorithm:
        case Algorithm.AGGLOMERATIVE_CLUSTERING:
            cluster_member_id = show_agglomerative_clustering(
                submissions,
                task_id,
                config,
                executable_path,
                output_path,
            )
        case Algorithm.SPECTRAL_CLUSTERING:
            cluster_member_id = show_spectral_clustering(submissions, task_id, config, executable_path, output_path)
        case _:
            st.error('The algorithm is not implemented')
            st.stop()

    st.code(
        submissions[submissions[EduColumnName.ID.value] == cluster_member_id].reset_index().loc[0, 'code'],
        language='kotlin',
    )


if __name__ == '__main__':
    main()
