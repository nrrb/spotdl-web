<template>
    <div>
      <h2>Download Spotify Track</h2>
      <form @submit.prevent="getSongInfo">
        <q-input clearable filled  color="purple-12" v-model="spotifyUrl" label="Spotify URL" />
        <q-btn 
            :loading="loadingSongInfo" 
            type="submit" 
            class="full-width"
        >
            Get Song Info
            <template v-slot:loading>
                <q-spinner-hourglass class="on-left" />
                Loading...
            </template>
        </q-btn>
      </form>

      <q-card class="song-info-card" flat bordered v-if="songInfo">
      <q-card-section horizontal>

        <q-card-section class="col-4 flex flex-center">
          <q-img
            class="rounded-borders"
            :src="songInfo.cover_url"
          >
          </q-img>  
        </q-card-section>
        <q-card-section>
            <div class="text-h5">{{ songInfo.name }}</div>
            <div class="text-h6">Artist: {{  songInfo.artist }}</div>
            <div class="text-h6">Album: {{ songInfo.album }}</div>
            <div class="text-h6">Time: {{ songInfo.duration }}</div>
            <div class="text-h6"><a :href="songInfo.url" target="_blank">Spotify Link</a></div>
        </q-card-section>
      </q-card-section>

      <q-separator />

      <q-card-actions>
        <q-btn 
            :loading="loadingDownload" 
            @click="downloadSong" 
            icon="cloud_download"
            v-if="!downloadUrl"
            color="yellow"
            class="full-width"
        >
            Get MP3
            <template v-slot:loading>
                <q-spinner-gears class="on-left" />
                Loading...
            </template>
        </q-btn>
        <q-btn
            icon="cloud_download"
            v-if="downloadUrl"
            :href="downloadUrl"
            color="green"
            class="full-width"
        >
            Download MP3
        </q-btn>
      </q-card-actions>
    </q-card>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        spotifyUrl: 'https://open.spotify.com/track/5cja2AdWxvJ7Ta693kYXwP?si=a69f9de178824aac',
        songInfo: null,
        downloadUrl: '',
        loadingSongInfo: false,
        loadingDownload: false
      };
    },
    methods: {
        getSongInfo() {
            this.songInfo = null;
            this.loadingSongInfo = true;
            fetch('http://127.0.0.1:5000/get-song-info', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({ spotify_url: this.spotifyUrl })
            })
            .then(response => response.json())
            .then(data => {
                if(data.task_id) {
                    this.startPollingSongInfo(data.task_id);
                } else {
                    this.loadingSongInfo = false;
                    console.error('Didn\'t get a task_id to query song info.');
                }
            })
            .catch(error => {
                this.loadingSongInfo = false;
                console.error('Error:', error);
            });
        },
        startPollingSongInfo(taskId) {
            const intervalId = setInterval(() => {
                fetch(`http://127.0.0.1:5000/task/song_info/${taskId}`)
                .then(response => response.json())
                .then(data => {
                if (data.state === 'PENDING') {
                    console.log('Getting song info...');
                } else if (data.state === 'SUCCESS') {
                    clearInterval(intervalId);
                    this.songInfo = data.result;
                    this.loadingSongInfo = false;
                } else {
                    this.loadingSongInfo = false;
                    clearInterval(intervalId);
                    console.error('Unknown data state from API while getting song info.');
                    console.log(data);
                }
                })
                .catch(error => {
                    this.loadingSongInfo = false;
                    console.error('Error getting song info:', error);
                    clearInterval(intervalId);
                });
            }, 5000);
        },
        downloadSong() {
            this.loadingDownload = true;
            fetch('http://127.0.0.1:5000/start-download', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({ spotify_url: this.spotifyUrl })
            })
            .then(response => response.json())
            .then(data => {
                if (data.task_id) {
                    console.log('Got task_id ${data.task_id}, now polling download...');
                    this.startPollingDownload(data.task_id);
                } else {
                    this.loadingDownload = false;
                    console.error('Didn\'t get a task_id to query download.');
                }
            })
            .catch(error => {
                this.loadingDownload = false;
                console.error('Error:', error);
            });
        },
        startPollingDownload(taskId) {
            const intervalId = setInterval(() => {
                fetch(`http://127.0.0.1:5000/task/download/${taskId}`)
                .then(response => response.json())
                .then(data => {
                if (data.state === 'PENDING') {
                    console.log('Download in progress...');
                    this.loadingDownload = true;
                } else if (data.state === 'SUCCESS') {
                    this.loadingDownload = false;
                    clearInterval(intervalId);
                    console.log('Download completed! File URL: ${data.result}');
                    this.downloadUrl = data.result;
                } else {
                    clearInterval(intervalId);
                    this.loadingDownload = false;
                    console.error('Unknown data state from API while downloading.');
                }
                })
                .catch(error => {
                    this.loadingDownload = false;
                    console.error('Error checking status:', error);
                    clearInterval(intervalId);
                });
            }, 5000);
        }
    }
  };
  </script>
  
  <style scoped>
  /* Add your styles here */
  </style>
  