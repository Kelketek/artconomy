<template>
  <div>
    <div v-if="asset.preview">
      <img :src="asset.preview.thumbnail" class="mb-2"/>
    </div>
    <v-expansion-panel v-if="compact">
      <v-expansion-panel-content>
        <div slot="header"><strong>Click to Read</strong></div>
        <v-card>
          <v-card-text v-html="mdRender(response)" v-if="response !== null" class="text-xs-left">
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-flex v-else-if="response" v-html="mdRender(response)" class="text-xs-left"></v-flex>
    <v-progress-circular indeterminate color="primary" v-if="!response" class="mb-2"></v-progress-circular>
  </div>
</template>

<script>
  import {artCall} from '../lib'
  import Markdown from '../mixins/markdown'

  export default {
    props: ['asset', 'compact'],
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