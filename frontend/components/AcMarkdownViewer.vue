<template>
  <v-row no-gutters  >
    <v-col cols="12" sm="6" offset-sm="3" md="4" offset-md="4">
      <v-img :src="asset.preview.thumbnail" class="mb-2" :aspect-ratio="1" v-if="asset.preview"/>
    </v-col>
    <v-col cols="12">
      <v-expansion-panel v-if="compact && !popOut">
        <v-expansion-panel-content>
          <div slot="header"><strong>Click to Read</strong></div>
          <v-card>
            <v-card-text v-html="mdRender(response)" v-if="response !== null" class="text-left">
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
        >
          <v-card tile>
            <v-toolbar flat dark color="primary">
              <v-btn icon @click.native="toggle = false" dark>
                <v-icon>close</v-icon>
              </v-btn>
              <v-toolbar-title></v-toolbar-title>
              <v-spacer/>
              <v-toolbar-items>
                <v-btn dark text @click.prevent="toggle = false">Close</v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text v-html="mdRender(response)">
            </v-card-text>
          </v-card>
        </v-dialog>
      </div>
      <v-col v-else-if="response">
        <v-card-text>
          <v-col v-html="mdRender(response)" class="text-left"></v-col>
        </v-card-text>
      </v-col>
      <v-progress-circular indeterminate color="primary" v-if="!response" class="mb-2"></v-progress-circular>
    </v-col>
  </v-row>
</template>

<script>
import {artCall} from '../lib'
import Formatting from '../mixins/formatting'

export default {
  props: ['asset', 'compact', 'popOut'],
  mixins: [Formatting],
  data() {
    return {
      response: null,
      toggle: false,
    }
  },
  methods: {
    loadFile(response) {
      this.response = response
    },
  },
  created() {
    artCall({url: this.asset.file.full, method: 'get'}).then(this.loadFile)
  },
}
</script>
