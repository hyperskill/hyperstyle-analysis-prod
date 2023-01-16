# JB Academy Data Description

### Topic
Example request:
```http request 
https://hyperskill.org/api/topics/1258
```
Example response:
```json
{
    "meta": {
        "page": 1,
        "has_next": false,
        "has_previous": false
    },
    "topics": [
        {
            "id": 405,
            "children": [],
            "depth": 6,
            "followers": [
                406,
                626,
                991,
                487,
                624,
                1601
            ],
            "has_steps": true,
            "hierarchy": [
                1162,
                1164,
                331,
                1202,
                427,
                991
            ],
            "parent_id": 991,
            "prerequisites": [
                399,
                415
            ],
            "progress_id": "2-405",
            "root_id": 1162,
            "root_subgroup_title": "Programming languages",
            "root_title": "Computer science",
            "theory": 5920,
            "title": "Comparisons",
            "topological_index": 159,
            "verification_step": 6374,
            "is_deprecated": false,
            "is_beta": false,
            "provider_id": 2
        }
    ]
}
```

### Step
Example request:
```http request 
https://hyperskill.org/api/steps/2435
```
Example response:
```json
{
    "meta": {
        "page": 1,
        "has_next": false,
        "has_previous": false
    },
    "steps": [
        {
            "block": {
                "name": "code",
                "text": "<p>You are playing a guessing game with a user. Imagine that you came up with an integer stored in a variable <code class=\"java\">set_number</code>.</p>\n\n<p>Check if <code class=\"java\">set_number</code> is equal to the product of two integers entered by the user.</p>\n\n<p><strong>The input format:</strong></p>\n\n<p>Two lines containing integer numbers for you to multiply.</p>\n\n<p><strong>The output format:</strong></p>\n\n<p><code class=\"java\">True</code> if the user guessed correctly and <code class=\"java\">False</code> otherwise.</p>",
                "video": null,
                "options": {
                    "execution_time_limit": 5,
                    "execution_memory_limit": 256,
                    "limits": {
                        "python3": {
                            "time": 15,
                            "memory": 256
                        }
                    },
                    "code_templates": {
                        "python3": "set_number = 6557"
                    },
                    "code_templates_header_lines_count": {
                        "python3": 0
                    },
                    "code_templates_footer_lines_count": {
                        "python3": 0
                    },
                    "code_templates_options": {},
                    "samples": [
                        [
                            "3\n11",
                            "False"
                        ]
                    ],
                    "is_run_user_code_allowed": true,
                    "language": ""
                },
                "table_of_contents": []
            },
            "can_abandon": false,
            "can_skip": false,
            "check_profile": "",
            "comments_statistics": [
                {
                    "thread": "comment",
                    "total_count": 32
                },
                {
                    "thread": "hint",
                    "total_count": 30
                },
                {
                    "thread": "useful link",
                    "total_count": 3
                },
                {
                    "thread": "solutions",
                    "total_count": 1062
                }
            ],
            "content_created_at": "2019-06-07T15:16:06Z",
            "id": 6382,
            "is_abandoned": false,
            "is_completed": true,
            "is_cribbed": false,
            "is_recommended": false,
            "is_next": false,
            "is_skipped": false,
            "last_completed_at": "2023-01-16T15:48:10.315355Z",
            "likes_statistics": [
                {
                    "subject": "",
                    "value": -2,
                    "total_count": 31
                },
                {
                    "subject": "",
                    "value": -1,
                    "total_count": 14
                },
                {
                    "subject": "",
                    "value": 0,
                    "total_count": 26
                },
                {
                    "subject": "",
                    "value": 1,
                    "total_count": 148
                },
                {
                    "subject": "",
                    "value": 2,
                    "total_count": 1199
                },
                {
                    "subject": "skip",
                    "value": 0,
                    "total_count": 5
                },
                {
                    "subject": "skip",
                    "value": 100,
                    "total_count": 144
                },
                {
                    "subject": "skip",
                    "value": 101,
                    "total_count": 18
                },
                {
                    "subject": "skip",
                    "value": 102,
                    "total_count": 78
                }
            ],
            "lesson_stepik_id": 236231,
            "position": 1,
            "seconds_to_complete": 139.01947099990463,
            "solved_by": 16571,
            "stage": null,
            "stepik_id": 746096,
            "success_rate": 0.412,
            "title": "Guessing game",
            "topic": 405,
            "topic_theory": 5920,
            "type": "practice",
            "updated_at": "2022-01-10T17:14:47.479947Z",
            "content_updated_at": "2020-04-27T15:46:44Z",
            "progress_updated_at": "2023-01-16T12:08:39.037001Z",
            "popular_ide": "PyCharmEdu",
            "project": null,
            "is_beta": false,
            "is_deprecated": false,
            "is_ide_compatible": true,
            "is_remote_tested": false,
            "error_issues_count": null,
            "warning_issues_count": null,
            "error_issues": [],
            "warning_issues": [],
            "can_see_admin_toolbar": false
        }
    ]
}
```

### User
Example request:
```http request 
https://hyperskill.org/api/users
```
```json
{
    "meta": {
        "page": 1,
        "has_next": false,
        "has_previous": false
    },
    "profiles": [
        {
            "id": 130072519,
            "avatar": "",
            "badge_title": "",
            "bio": "",
            "fullname": "Maria Tigina",
            "gamification": {
                "active_days": 29,
                "daily_step_completed_count": 4,
                "passed_problems": 104,
                "passed_projects": 0,
                "passed_topics": 5,
                "progress_updated_at": "2023-01-12T12:55:53.441591Z",
                "activities_count": 249,
                "passed_activities": 5,
                "hypercoins": 158,
                "last_code_problem_client": "web",
                "notifications_unread": 1,
                "passed_problems_in_ide": 1,
                "passed_stages": 0,
                "passed_theories": 81,
                "seconds_to_reach_stage": 39824,
                "topics_repetitions": {
                    "repetitions_count": 4,
                    "repeated_today_count": 0
                }
            },
            "invitation_code": "e52900751",
            "comments_posted": {
                "comment": 0,
                "hint": 0,
                "useful link": 0,
                "solutions": 0
            },
            "username": "id130072519",
            "completed_tracks": [],
            "country": null,
            "languages": [],
            "experience": "",
            "github_username": "",
            "linkedin_username": "",
            "twitter_username": "",
            "reddit_username": "",
            "facebook_username": "",
            "discord_username": "",
            "discord_id": null,
            "visibility": "public",
            "cover": "",
            "selected_tracks": [
                2,
                3,
                8,
                49
            ],
            "daily_pace_minutes": 60,
            "daily_step": 6642,
            "date_registered": "2021-09-01T11:31:27.274287Z",
            "email": "maria.tigina@jetbrains.com",
            "kind": "person",
            "features": {
                "projects.beta_project": true,
                "learning_path.diagnostic": true,
                "topic.suggest_problems": true,
                "study_groups": true,
                "backend.track_activities": true,
                "steps.dataset_in_ide": true,
                "products.profile_covers": true,
                "progress.use_ws_only": true,
                "study_plan.stage_feedback": true,
                "learning_path.track_milestone": true,
                "backend.cancel_jetsales_subscription": true,
                "subscriptions_info.use_ws": true,
                "discord_study_groups": true,
                "b2b.landing_page": true,
                "ui.feedback-list": true,
                "organization.invite_modal": true,
                "studio.can_update_steps": true,
                "ui.seconds_to_complete_stage_section": true,
                "ui.trackview_select_btn_no_scroll": true,
                "ui.trackview_no_extra_floating_enroll_now": true,
                "diagnostics.hide_navbar_nav": true,
                "study_plan.daily_challenge_show_cond": true,
                "loginform.new_design": true,
                "auth.join_as_individual": true,
                "study_plan.section.return_all_activities": true,
                "topic.redesign_completion_page": true,
                "subscriptions.personal_active_trial_primary": true,
                "steps.hide_code_quality": true,
                "subscriptions.registration_without_track_automatically_start_trial": true,
                "frontend.track_cacheable_requests": true,
                "pricing.book_demo": true
            },
            "is_anonymous": false,
            "can_issue_certificate": true,
            "is_beta": true,
            "is_biased": true,
            "is_diagnosed": false,
            "is_email_verified": true,
            "is_guest": false,
            "is_terms_accepted": false,
            "is_staff": false,
            "is_subscribed_to_notifications": true,
            "is_testee": true,
            "track_id": 2,
            "track_title": "Python Core",
            "project": 112,
            "subscribed_for_marketing": true,
            "free_till": null,
            "isic_id": "",
            "isic_name": "",
            "isic_status": 0
        }
    ]
}
```

### Submissions
Example request:
```http request
https://hyperskill.org/api/submissions?user=130072519
```
Example response:
```json
{
  "meta": {
    "page": 1,
    "has_next": true,
    "has_previous": false
  },
  "submissions": [
    {
      "id": 94702240,
      "attempt": 75267259,
      "eta": 0,
      "feedback": "Failed test #3 of 8. Wrong answer\n",
      "hint": "Failed test #3 of 8. Wrong answer\n",
      "reply": {
        "language": "python3",
        "code": "set_number = 6557\n\nprint('False')\n"
      },
      "initial_status": "wrong",
      "status": "wrong",
      "client": "web",
      "step": 6382,
      "time": "2023-01-16T12:55:36.346446Z",
      "can_download_test_set": true,
      "is_downloaded_test": false,
      "is_free_test": true,
      "next_free_test_available_at": "2023-01-16T17:14:37.440704+00:00",
      "is_samples_test": false,
      "failed_test_number": 3,
      "solving_context": "default",
      "is_published": false,
      "user_id": 130072519
    },
    {
      "id": 94702226,
      "attempt": 75267259,
      "eta": 0,
      "feedback": "Failed test #1 of 8. Wrong answer\n\nThis is a sample test from the problem statement!\n\nTest input:\n3\n11\nCorrect output:\nFalse\n\nYour code output:\nTrue\n",
      "hint": "Failed test #1 of 8. Wrong answer\n\nThis is a sample test from the problem statement!\n\nTest input:\n3\n11\nCorrect output:\nFalse\n\nYour code output:\nTrue\n",
      "reply": {
        "language": "python3",
        "code": "set_number = 6557\n\nprint('True')\n"
      },
      "initial_status": "wrong",
      "status": "wrong",
      "client": "web",
      "step": 6382,
      "time": "2023-01-16T12:55:22.992877Z",
      "can_download_test_set": false,
      "is_downloaded_test": false,
      "is_free_test": false,
      "next_free_test_available_at": null,
      "is_samples_test": true,
      "failed_test_number": 1,
      "solving_context": "default",
      "is_published": false,
      "user_id": 130072519
    },
    {
      "id": 94698922,
      "attempt": 75264609,
      "eta": 0,
      "feedback": {
        "message": "",
        "code_style": {
          "quality": {
            "code": "MODERATE",
            "text": "Code quality (beta): MODERATE"
          },
          "errors": [
            {
              "code": "E225",
              "text": "missing whitespace around operator",
              "line": "x =int(input())",
              "line_number": 2,
              "column_number": 3,
              "category": "CODE_STYLE",
              "difficulty": "EASY",
              "influence_on_penalty": 0
            }
          ]
        }
      },
      "hint": "",
      "reply": {
        "language": "python3",
        "code": "set_number = 6557\n\nx =int(input())\ny = int(input())\nprint(set_number == x * y)"
      },
      "initial_status": "correct",
      "status": "correct",
      "client": "Python",
      "step": 6382,
      "time": "2023-01-16T12:08:39.037001Z",
      "can_download_test_set": false,
      "is_downloaded_test": false,
      "is_free_test": false,
      "next_free_test_available_at": null,
      "is_samples_test": false,
      "failed_test_number": null,
      "solving_context": "default",
      "is_published": false,
      "user_id": 130072519
    },
    {
      "id": 94698876,
      "attempt": 75264138,
      "eta": 0,
      "feedback": {
        "message": "",
        "code_style": {
          "quality": {
            "code": "MODERATE",
            "text": "Code quality (beta): MODERATE"
          },
          "errors": [
            {
              "code": "E225",
              "text": "missing whitespace around operator",
              "line": "x =int(input())",
              "line_number": 2,
              "column_number": 3,
              "category": "CODE_STYLE",
              "difficulty": "EASY",
              "influence_on_penalty": 0
            }
          ]
        }
      },
      "hint": "",
      "reply": {
        "language": "python3",
        "code": "set_number = 6557\n\nx =int(input())\ny = int(input())\nprint(set_number == x * y)\n"
      },
      "initial_status": "correct",
      "status": "correct",
      "client": "web",
      "step": 6382,
      "time": "2023-01-16T12:07:49.493087Z",
      "can_download_test_set": false,
      "is_downloaded_test": false,
      "is_free_test": false,
      "next_free_test_available_at": null,
      "is_samples_test": false,
      "failed_test_number": null,
      "solving_context": "default",
      "is_published": false,
      "user_id": 130072519
    }
  ]
}
```
