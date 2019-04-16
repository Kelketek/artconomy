<template>
  <div>
    <ac-share-button ref="shareButton" title="Sharable thing!"></ac-share-button>
  </div>
</template>
<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import AcShareButton from '../AcShareButton.vue'
  @Component({
    components: {AcShareButton},
  })
export default class DummyShare extends Vue {
}
</script>
