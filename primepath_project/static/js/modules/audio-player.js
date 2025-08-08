/**
 * Audio Player Module
 * Handles audio playback for questions in tests
 * Replaces inline audio functions from student_test.html
 */

(function(window) {
    'use strict';

    window.PrimePath = window.PrimePath || {};
    window.PrimePath.modules = window.PrimePath.modules || {};

    const BaseModule = window.PrimePath.modules.BaseModule;

    /**
     * Audio Player Module
     * Manages audio playback, progress tracking, and controls
     */
    class AudioPlayer extends BaseModule {
        constructor(options = {}) {
            super('AudioPlayer', options);
            
            // Currently playing audio
            this.activeAudioId = null;
            this.activeAudioElement = null;
            
            // Playback settings
            this.allowMultiple = options.allowMultiple || false;
            this.autoStop = options.autoStop !== false; // Auto-stop when switching
            
            // Progress update interval
            this.progressInterval = null;
            
            // Track played audio for analytics
            this.playedAudios = new Set();
            this.playCount = new Map();
        }

        /**
         * Initialize audio player
         */
        init() {
            if (this.initialized) return;
            
            this.setupEventHandlers();
            this.setupKeyboardControls();
            
            super.init();
        }

        /**
         * Play or pause audio
         * @param {string|number} audioId Audio element ID
         * @param {Object} options Playback options
         */
        async play(audioId, options = {}) {
            const audioElement = document.getElementById(`audio-element-${audioId}`);
            const playButton = document.getElementById(`audio-play-${audioId}`);
            const iconElement = document.getElementById(`audio-icon-${audioId}`);
            const progressTrack = document.getElementById(`progress-track-${audioId}`);
            
            if (!audioElement) {
                this.log('error', `Audio element not found: ${audioId}`);
                return;
            }
            
            // Stop other audio if not allowing multiple
            if (!this.allowMultiple && this.activeAudioId && this.activeAudioId !== audioId) {
                await this.stop(this.activeAudioId);
            }
            
            if (audioElement.paused) {
                try {
                    // Start playing
                    await audioElement.play();
                    
                    this.activeAudioId = audioId;
                    this.activeAudioElement = audioElement;
                    
                    // Update UI
                    if (playButton) playButton.classList.add('playing');
                    if (iconElement) iconElement.textContent = '⏸';
                    if (progressTrack) progressTrack.classList.add('active');
                    
                    // Track playback
                    this.playedAudios.add(audioId);
                    this.playCount.set(audioId, (this.playCount.get(audioId) || 0) + 1);
                    
                    // Start progress tracking
                    this.startProgressTracking(audioId);
                    
                    this.emit('play', {
                        audioId,
                        duration: audioElement.duration,
                        playCount: this.playCount.get(audioId)
                    });
                    
                } catch (error) {
                    this.log('error', `Failed to play audio: ${audioId}`, error);
                    this.emit('error', { audioId, error: error.message });
                }
            } else {
                // Pause audio
                this.pause(audioId);
            }
        }

        /**
         * Pause audio
         * @param {string|number} audioId Audio element ID
         */
        pause(audioId) {
            const audioElement = document.getElementById(`audio-element-${audioId}`);
            const playButton = document.getElementById(`audio-play-${audioId}`);
            const iconElement = document.getElementById(`audio-icon-${audioId}`);
            
            if (!audioElement) return;
            
            audioElement.pause();
            
            // Update UI
            if (playButton) playButton.classList.remove('playing');
            if (iconElement) iconElement.textContent = '▶';
            
            // Stop progress tracking
            this.stopProgressTracking();
            
            this.emit('pause', { audioId, currentTime: audioElement.currentTime });
        }

        /**
         * Stop audio and reset
         * @param {string|number} audioId Audio element ID
         */
        async stop(audioId) {
            // Ensure audioId is a string
            audioId = String(audioId);
            
            const audioElement = document.getElementById(`audio-element-${audioId}`);
            const playButton = document.getElementById(`audio-play-${audioId}`);
            const iconElement = document.getElementById(`audio-icon-${audioId}`);
            const progressTrack = document.getElementById(`progress-track-${audioId}`);
            const progressFill = document.getElementById(`progress-fill-${audioId}`);
            
            if (!audioElement) return;
            
            // Stop playback
            audioElement.pause();
            audioElement.currentTime = 0;
            
            // Update UI
            if (playButton) playButton.classList.remove('playing');
            if (iconElement) iconElement.textContent = '▶';
            if (progressTrack) progressTrack.classList.remove('active');
            if (progressFill) progressFill.style.width = '0%';
            
            // Clear active audio
            if (this.activeAudioId === audioId) {
                this.activeAudioId = null;
                this.activeAudioElement = null;
            }
            
            // Stop progress tracking
            this.stopProgressTracking();
            
            this.emit('stop', { audioId });
        }

        /**
         * Stop all playing audio
         */
        async stopAll() {
            if (this.activeAudioId) {
                await this.stop(this.activeAudioId);
            }
            
            // Also stop any other audio elements that might be playing
            document.querySelectorAll('audio').forEach(audio => {
                if (!audio.paused) {
                    audio.pause();
                    audio.currentTime = 0;
                }
            });
            
            this.emit('stopAll');
        }

        /**
         * Start tracking audio progress
         * @param {string|number} audioId Audio element ID
         */
        startProgressTracking(audioId) {
            this.stopProgressTracking(); // Clear any existing interval
            
            this.progressInterval = setInterval(() => {
                this.updateProgress(audioId);
            }, 100); // Update every 100ms for smooth progress
        }

        /**
         * Stop tracking audio progress
         */
        stopProgressTracking() {
            if (this.progressInterval) {
                clearInterval(this.progressInterval);
                this.progressInterval = null;
            }
        }

        /**
         * Update audio progress bar
         * @param {string|number} audioId Audio element ID
         */
        updateProgress(audioId) {
            const audioElement = document.getElementById(`audio-element-${audioId}`);
            const progressFill = document.getElementById(`progress-fill-${audioId}`);
            
            if (!audioElement || !progressFill) return;
            
            if (audioElement.duration) {
                const progress = (audioElement.currentTime / audioElement.duration) * 100;
                progressFill.style.width = `${progress}%`;
                
                this.emit('progress', {
                    audioId,
                    currentTime: audioElement.currentTime,
                    duration: audioElement.duration,
                    progress: progress
                });
            }
        }

        /**
         * Handle audio ended event
         * @param {string|number} audioId Audio element ID
         */
        handleAudioEnded(audioId) {
            this.stop(audioId);
            this.emit('ended', { audioId });
        }

        /**
         * Set volume for all audio elements
         * @param {number} volume Volume level (0-1)
         */
        setVolume(volume) {
            volume = Math.max(0, Math.min(1, volume));
            
            document.querySelectorAll('audio').forEach(audio => {
                audio.volume = volume;
            });
            
            this.emit('volumeChanged', { volume });
        }

        /**
         * Get playback statistics
         * @returns {Object} Playback stats
         */
        getStats() {
            return {
                playedCount: this.playedAudios.size,
                playedAudios: Array.from(this.playedAudios),
                playCounts: Object.fromEntries(this.playCount),
                currentlyPlaying: this.activeAudioId
            };
        }

        /**
         * Setup event handlers for audio controls
         */
        setupEventHandlers() {
            const delegation = window.PrimePath.utils.EventDelegation;
            
            // Play button clicks
            delegation.onClick('[data-audio-play]', (e) => {
                const audioId = e.currentTarget.dataset.audioPlay;
                this.play(audioId);
            });
            
            // Audio ended events (using event delegation)
            document.addEventListener('ended', (e) => {
                if (e.target.tagName === 'AUDIO') {
                    const audioId = e.target.id.replace('audio-element-', '');
                    this.handleAudioEnded(audioId);
                }
            }, true);
            
            // Audio time update events
            document.addEventListener('timeupdate', (e) => {
                if (e.target.tagName === 'AUDIO' && e.target.id === `audio-element-${this.activeAudioId}`) {
                    const audioId = e.target.id.replace('audio-element-', '');
                    this.updateProgress(audioId);
                }
            }, true);
            
            // Stop audio when navigating away
            window.addEventListener('beforeunload', () => {
                this.stopAll();
            });
        }

        /**
         * Setup keyboard controls for audio
         */
        setupKeyboardControls() {
            if (!this.options.enableKeyboard) return;
            
            document.addEventListener('keydown', (e) => {
                // Ignore if typing in input/textarea
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                
                switch(e.key) {
                    case ' ':
                        // Space bar to play/pause
                        if (this.activeAudioId) {
                            e.preventDefault();
                            this.play(this.activeAudioId);
                        }
                        break;
                    case 'Escape':
                        // Escape to stop
                        if (this.activeAudioId) {
                            this.stop(this.activeAudioId);
                        }
                        break;
                }
            });
        }

        /**
         * Migrate existing onclick handlers to data attributes
         * Call this after DOM is loaded to convert legacy audio controls
         */
        migrateInlineHandlers() {
            // Convert playQuestionAudio onclick handlers
            document.querySelectorAll('[onclick*="playQuestionAudio"]').forEach(element => {
                const match = element.getAttribute('onclick').match(/playQuestionAudio\((\d+)\)/);
                if (match) {
                    const audioId = match[1];
                    element.setAttribute('data-audio-play', audioId);
                    element.removeAttribute('onclick');
                }
            });
            
            // Convert audioFinished onended handlers
            document.querySelectorAll('audio[onended*="audioFinished"]').forEach(audio => {
                const match = audio.getAttribute('onended').match(/audioFinished\((\d+)\)/);
                if (match) {
                    audio.removeAttribute('onended');
                    // Event listener will handle it
                }
            });
            
            // Convert updateAudioProgress ontimeupdate handlers
            document.querySelectorAll('audio[ontimeupdate*="updateAudioProgress"]').forEach(audio => {
                audio.removeAttribute('ontimeupdate');
                // Event listener will handle it
            });
        }

        /**
         * Destroy module and cleanup
         */
        destroy() {
            this.stopAll();
            this.stopProgressTracking();
            this.playedAudios.clear();
            this.playCount.clear();
            
            super.destroy();
        }
    }

    // Export to PrimePath namespace
    window.PrimePath.modules.AudioPlayer = AudioPlayer;

    // Create convenience methods for backward compatibility
    window.playQuestionAudio = function(audioId) {
        if (!window.audioPlayer) {
            window.audioPlayer = new AudioPlayer();
            window.audioPlayer.init();
        }
        window.audioPlayer.play(audioId);
    };
    
    window.audioFinished = function(audioId) {
        if (window.audioPlayer) {
            window.audioPlayer.handleAudioEnded(audioId);
        }
    };
    
    window.updateAudioProgress = function(audioId) {
        if (window.audioPlayer) {
            window.audioPlayer.updateProgress(audioId);
        }
    };
    
    window.stopQuestionAudio = function(audioId) {
        if (window.audioPlayer) {
            window.audioPlayer.stop(audioId);
        }
    };
    
    window.stopAllQuestionAudio = function() {
        if (window.audioPlayer) {
            window.audioPlayer.stopAll();
        }
    };

    // Also export for module systems
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = AudioPlayer;
    }

})(window);