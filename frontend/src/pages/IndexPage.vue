<template>
  <q-page class="row items-center justify-evenly">
    <SpotifyDownloader />
  </q-page>
</template>

<script setup lang="ts">
import SpotifyDownloader from 'components/SpotifyDownloader.vue';

defineOptions({
  name: 'IndexPage'
});
</script>
