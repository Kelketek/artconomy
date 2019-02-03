<template>
  <div>
    <div v-if="asset.preview">
      <img :src="asset.preview.thumbnail" class="mb-2"/>
    </div>
    <v-expansion-panel v-if="compact && !popOut">
      <v-expansion-panel-content>
        <div slot="header"><strong>Click to Read</strong></div>
        <v-card>
          <v-card-text v-html="mdRender(response)" v-if="response !== null" class="text-xs-left">
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <div v-else-if="popOut">
      <v-btn @click="toggle=true">Click to read</v-btn>
      <v-dialog
          v-model="toggle"
          fullscreen
          ref="dialog"
          transition="dialog-bottom-transition"
          :overlay="false"
          scrollable
          v-else-if=""
      >
        <v-card tile>
          <v-toolbar card dark color="primary">
            <v-btn icon @click.native="toggle = false" dark>
              <v-icon>close</v-icon>
            </v-btn>
            <v-toolbar-title></v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-btn dark flat @click.prevent="toggle = false">Close</v-btn>
            </v-toolbar-items>
          </v-toolbar>
          <v-card-text v-html="mdRender(response)">
          </v-card-text>
        </v-card>
      </v-dialog>
    </div>
    <v-flex v-else-if="response" v-html="mdRender(response)" class="text-xs-left"></v-flex>
    <v-progress-circular indeterminate color="primary" v-if="!response" class="mb-2"></v-progress-circular>
  </div>
</template>

<script>
  import {artCall} from '../lib'
  import Markdown from '../mixins/markdown'

  export default {
    props: ['asset', 'compact', 'popOut'],
    mixins: [Markdown],
    data () {
      return {
        response: null,
        toggle: false
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