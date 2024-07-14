<template>
  <div>
    <ac-share-button ref="shareButton" title="Sharable thing!" media-url="https://example.com/thing.jpg"
                     :clean="true"></ac-share-button>
  </div>
</template>
<script setup lang="ts">
import AcShareButton from '../AcShareButton.vue'
</script>
