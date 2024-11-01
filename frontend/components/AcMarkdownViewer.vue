<template>
  <v-row no-gutters>
    <v-col cols="12" sm="6" offset-sm="3" md="4" offset-md="4">
      <v-img :src="asset.preview.thumbnail" class="mb-2" :aspect-ratio="1" v-if="asset.preview" alt="An example image loaded via Markdown."/>
    </v-col>
    <v-col cols="12">
      <v-expansion-panel v-if="compact && !popOut">
        <v-expansion-panel-title><strong>Click to Read</strong></v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-card>
            <v-card-text v-html="md.render(response)" v-if="response !== null" class="text-left">
            </v-card-text>
          </v-card>
        </v-expansion-panel-text>
      </v-expansion-panel>
      <div v-else-if="popOut">
        <v-btn @click="toggle=true" variant="flat">Click to read</v-btn>
        <v-dialog
            v-model="toggle"
            fullscreen
            ref="dialog"
            transition="dialog-bottom-transition"
            :overlay="false"
            scrollable
            :attach="modalTarget"
        >
          <v-card tile>
            <v-toolbar flat dark color="primary">
              <v-btn icon @click="toggle = false" dark>
                <v-icon :icon="mdiClose"/>
              </v-btn>
              <v-toolbar-title></v-toolbar-title>
              <v-spacer/>
              <v-toolbar-items>
                <v-btn dark variant="text" @click.prevent="toggle = false">Close</v-btn>
              </v-toolbar-items>
            </v-toolbar>
            <v-card-text v-html="md.render(response)" v-if="response !== null">
            </v-card-text>
          </v-card>
        </v-dialog>
      </div>
      <v-col v-else-if="response">
        <v-card-text>
          <v-col v-html="md.render(response)" class="text-left"></v-col>
        </v-card-text>
      </v-col>
      <v-progress-circular indeterminate color="primary" v-if="!response" class="mb-2"></v-progress-circular>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import {artCall} from '../lib/lib.ts'
import {mdiClose} from '@mdi/js'
import {md} from '@/lib/markdown.ts'
import {useTargets} from '@/plugins/targets.ts'
import type {Asset} from '@/types/main'

const props = defineProps<{asset: Asset, compact?: boolean, popOut?: boolean}>()
const response = ref<string|null>(null)
const toggle = ref(false)
const {modalTarget} = useTargets()

const loadFile = (responseText: string) => {
  response.value = responseText
}

artCall({
  url: props.asset.file.full,
  method: 'get',
}).then(loadFile)
</script>
