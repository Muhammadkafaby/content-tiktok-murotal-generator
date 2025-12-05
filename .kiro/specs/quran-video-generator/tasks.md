# Implementation Plan

- [x] 1. Setup project structure dan dependencies


  - [x] 1.1 Create project directory structure (api, generator, tiktok, frontend)


    - Setup FastAPI backend structure
    - Setup React/Vite frontend structure
    - Create shared config files
    - _Requirements: 4.1_
  - [x] 1.2 Create Dockerfile dan docker-compose.yml


    - Configure multi-stage build untuk frontend + backend
    - Setup volume mounts untuk videos, backgrounds, db, sessions
    - Configure shm_size untuk Playwright
    - _Requirements: 4.1, 4.2, 4.4_
  - [x] 1.3 Setup Python dependencies (requirements.txt)


    - FastAPI, uvicorn, SQLAlchemy
    - MoviePy, Pillow, FFmpeg-python
    - APScheduler, httpx, playwright
    - _Requirements: 4.1_

- [x] 2. Implement database models dan storage

  - [x] 2.1 Create SQLite database schema


    - Video model dengan semua fields
    - Settings model
    - GenerateJob model
    - TikTokSession model
    - PostHistory model
    - _Requirements: 4.3, 4.4_
  - [x] 2.2 Implement repository layer untuk CRUD operations


    - VideoRepository
    - SettingsRepository
    - JobRepository
    - _Requirements: 4.3_
  - [x] 2.3 Write property test for data persistence


    - **Property 9: Data Persistence**
    - **Validates: Requirements 4.3, 4.4**

- [x] 3. Implement Quran API integration

  - [x] 3.1 Create QuranService untuk fetch ayat data

    - Fetch teks Arab dari Al-Quran Cloud API
    - Fetch terjemahan Indonesia
    - Download audio murotal per ayat
    - _Requirements: 1.2_
  - [x] 3.2 Implement random ayat selection dengan duplicate tracking

    - Random selection dari 6236 ayat
    - Track ayat yang sudah digunakan
    - _Requirements: 1.1, 1.5_
  - [x] 3.3 Write property tests for Quran API


    - **Property 1: Valid Ayat Selection**
    - **Property 2: Complete Data Retrieval**
    - **Validates: Requirements 1.1, 1.2**

- [x] 4. Implement Video Generator service

  - [x] 4.1 Create background video manager

    - Load dan manage koleksi background videos
    - Random selection dari koleksi
    - _Requirements: 3.3_
  - [x] 4.2 Implement text overlay generator

    - Render teks Arab dengan font kaligrafi
    - Render terjemahan Indonesia
    - Position text properly pada video
    - _Requirements: 3.4, 3.5_
  - [x] 4.3 Implement video composition dengan FFmpeg/MoviePy

    - Combine background video + text overlay + audio
    - Output MP4 dengan rasio 9:16 (1080x1920)
    - _Requirements: 1.3, 1.4_

  - [x] 4.4 Write property tests for video generator

    - **Property 3: Video Output Format Compliance**
    - **Property 6: Background Selection Validity**
    - **Property 7: Translation Inclusion**
    - **Validates: Requirements 1.4, 3.3, 3.5**

- [x] 5. Implement Audio-Text Synchronization

  - [x] 5.1 Add librosa dan pydub dependencies
    - Add librosa untuk audio analysis
    - Add pydub untuk audio manipulation
    - _Requirements: 8.1_

  - [x] 5.2 Create AudioSyncService untuk timing calculation
    - Implement calculate_text_timing() untuk proportional timing
    - Calculate arab_start, translation_start, fade timings
    - Ensure text duration matches audio duration
    - _Requirements: 8.1, 8.2, 8.5_

  - [x] 5.3 Implement audio segment detection
    - Use librosa to detect silence intervals
    - Split text into segments based on audio pauses
    - Handle ayat panjang dengan multiple segments
    - _Requirements: 8.3_

  - [x] 5.4 Implement text animation with fade effects
    - Create fade-in animation untuk teks Arab
    - Create fade-in animation untuk terjemahan
    - Create fade-out animation untuk semua teks
    - Ensure smooth transitions (0.3-1.0 second duration)
    - _Requirements: 8.4_

  - [x] 5.5 Integrate sync service dengan video generator
    - Modify video_generator.py untuk use AudioSyncService
    - Apply timing data ke text overlays
    - Ensure teks muncul sinkron dengan audio
    - _Requirements: 8.1, 8.2, 8.5_

  - [x] 5.6 Write property tests for audio sync



    - **Property 19: Audio-Text Synchronization**
    - **Property 20: Translation Timing Sequence**
    - **Property 21: Text Duration Alignment**
    - **Property 22: Smooth Text Animation**
    - **Property 23: Segment Timing Validity**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 6. Checkpoint - Ensure core video generation with sync works



  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement REST API endpoints

  - [x] 7.1 Create video endpoints
    - GET /api/videos - list dengan pagination
    - GET /api/videos/{id} - detail
    - GET /api/videos/{id}/download - download file
    - DELETE /api/videos/{id} - delete
    - _Requirements: 2.1, 2.3_

  - [ ] 7.2 Create generate endpoints
    - POST /api/generate - trigger generate
    - GET /api/generate/status - check status
    - POST /api/generate/cancel - cancel job
    - _Requirements: 2.2, 2.4, 2.5_

  - [ ] 7.3 Create settings endpoints
    - GET /api/settings
    - PUT /api/settings
    - _Requirements: 3.1, 3.2_

  - [ ] 7.4 Create stats endpoint
    - GET /api/stats - total videos, storage used, dll
    - _Requirements: 5.4_

  - [ ] 7.5 Write property tests for API
    - **Property 4: Batch Uniqueness**
    - **Property 8: Progress Accuracy**
    - **Validates: Requirements 1.5, 2.5**

- [ ] 8. Implement Task Scheduler
  - [ ] 8.1 Setup APScheduler dengan SQLite job store
    - Configure persistent job storage
    - Setup cron-based scheduling
    - _Requirements: 5.1_

  - [ ] 8.2 Implement scheduled video generation
    - Auto-generate berdasarkan schedule
    - Record history di database
    - _Requirements: 5.1, 5.3_

  - [ ] 8.3 Write property tests for scheduler
    - **Property 11: Scheduler Execution**
    - **Property 12: Generation History Tracking**
    - **Validates: Requirements 5.1, 5.3**

- [ ] 9. Implement TikTok Auto-Posting service
  - [x] 9.1 Setup Playwright untuk headless browser
    - Install browser dependencies
    - Configure browser launch options
    - _Requirements: 6.1_

  - [ ] 9.2 Implement TikTok login dan session management
    - Login flow dengan QR code atau manual
    - Save dan load session cookies
    - Session validation
    - _Requirements: 6.1, 6.6_

  - [ ] 9.3 Implement video upload automation
    - Navigate ke upload page
    - Upload video file
    - Fill caption dan hashtags
    - Click post button
    - _Requirements: 6.2, 6.3_

  - [ ] 9.4 Implement posting status tracking
    - Record success/failed status
    - Retry logic untuk failed posts
    - _Requirements: 6.4, 6.5_

  - [x] 9.5 Write property tests for TikTok service
    - **Property 14: TikTok Session Persistence**
    - **Property 15: TikTok Upload Completion**
    - **Property 17: Post Status Tracking**
    - **Validates: Requirements 6.1, 6.2, 6.4, 6.5**

- [ ] 10. Implement AI Caption Generator
  - [ ] 10.1 Create OpenAI integration service
    - Setup OpenAI API client
    - Create prompt template untuk caption generation
    - _Requirements: 7.1_

  - [ ] 10.2 Implement caption generation logic
    - AI mode: generate engaging caption dengan hikmah
    - Template mode: simple format caption
    - Fallback mechanism jika AI fails
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [ ] 10.3 Write property tests for caption generator
    - **Property 16: Caption Generation**
    - **Property 18: AI Caption Content Validity**
    - **Validates: Requirements 6.3, 7.2**

- [ ] 11. Checkpoint - Ensure backend services work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement Frontend (React/Vite)
  - [x] 12.1 Setup React project dengan Vite
    - Install dependencies (React, TailwindCSS, axios)
    - Configure routing
    - _Requirements: 2.1_

  - [ ] 12.2 Create Dashboard page
    - Display list of generated videos
    - Show statistics (total videos, storage)
    - Show recent activity
    - _Requirements: 2.1, 5.3_

  - [x] 12.3 Create Generate page
    - Generate button untuk single video
    - Batch generate dengan input jumlah
    - Progress indicator
    - _Requirements: 2.2, 2.4, 2.5_

  - [ ] 12.4 Create Videos gallery page
    - Grid view of all videos
    - Video preview player
    - Download button
    - Delete button
    - _Requirements: 2.3_

  - [ ] 12.5 Create Settings page
    - Qari selection dropdown
    - Scheduler configuration
    - TikTok account setup
    - Caption mode selection (AI/Template)
    - _Requirements: 3.1, 5.2, 6.6, 7.1_

  - [ ] 12.6 Create TikTok integration page
    - Login status display
    - Manual post button
    - Posting history
    - _Requirements: 6.4, 6.6_

- [ ] 13. Implement Error Handling dan Logging
  - [ ] 13.1 Setup logging system
    - Configure Python logging
    - Log to file dan console
    - _Requirements: 4.5_

  - [ ] 13.2 Implement storage monitoring
    - Check disk space before generate
    - Alert when storage < 1GB
    - _Requirements: 5.4_

  - [ ] 13.3 Write property tests for error handling
    - **Property 10: Error Logging**
    - **Property 13: Storage Alert Threshold**
    - **Validates: Requirements 4.5, 5.4**

- [ ] 14. Final integration dan Docker build
  - [ ] 14.1 Build frontend dan integrate dengan backend
    - Build React app
    - Serve static files dari FastAPI
    - _Requirements: 4.1_

  - [ ] 14.2 Test Docker container locally
    - Build image
    - Run dengan docker-compose
    - Verify all features work
    - _Requirements: 4.1, 4.2_

  - [ ] 14.3 Add sample background videos
    - Download beberapa video pemandangan dari Pexels
    - Add ke backgrounds volume
    - _Requirements: 3.3_

- [ ] 15. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
