<template>
  <v-container>
    <v-row no-gutters >
      <v-col>
        <v-card>
          <v-card-text>
            <p>This page has moved. Redirecting you...</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import {setMetaContent} from '@/lib/lib'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class Redirect extends Vue {
  @Prop({required: true})
  public endpoint!: string

  public get portString() {
    if (window.location.port) {
      return ':80'
    }
    return ''
  }

  public get url() {
    return `${window.location.protocol}//${window.location.host}${this.portString}${this.endpoint}`
  }

  public created() {
    setMetaContent('prerender-status-code', '', {content: this.url})
    // @ts-ignore
    if (!window.PRERENDERING) {
      this.$router.replace(this.endpoint)
    }
  }
}
</script>
