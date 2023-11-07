<template>
  <div>
    <ac-share-button ref="shareButton" title="Sharable thing!" media-url="https://example.com/thing.jpg"
                     :clean="true"></ac-share-button>
  </div>
</template>
<script lang="ts">
import {Component, toNative, Vue} from 'vue-facing-decorator'
import AcShareButton from '../AcShareButton.vue'

@Component({
  components: {AcShareButton},
})
class DummyShare extends Vue {
}

export default toNative(DummyShare)
</script>
