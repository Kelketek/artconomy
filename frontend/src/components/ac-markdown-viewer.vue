<template>
  <div>
    <div v-if="asset.preview">
      <img :src="asset.preview.thumbnail" class="mb-2"/>
    </div>
    <div v-html="mdRender(response)" v-if="response !== null" class="text-xs-left">
    </div>
    <v-progress-circular indeterminate color="primary" v-if="!response" class="mb-2"></v-progress-circular>
  </div>
</template>

<script>
  import {artCall} from '../lib'
  import Markdown from '../mixins/markdown'

  export default {
    props: ['asset'],
    mixins: [Markdown],
    data () {
      return {
        response: null
      }
    },
    methods: {
      loadFile (response) {
        this.response = response
      }
    },
    created () {
      artCall(this.asset.file.full, 'GET', undefined, this.loadFile)
    }
  }
</script>