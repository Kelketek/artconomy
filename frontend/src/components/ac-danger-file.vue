<template>
  <v-alert :value="true" type="error">Warning: This is a dangerous file type (.{{ext}}). Be cautious when downloading and running! If in doubt, consult a professional!</v-alert>
</template>

<script>
  import {getExt} from '../lib'

  export default {
    name: 'ac-danger-file',
    props: ['asset'],
    computed: {
      ext () {
        return getExt(this.asset.file.full)
      }
    }
  }
</script>