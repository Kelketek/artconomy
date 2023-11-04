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
import {RawLocation} from 'vue-router'

@Component
export default class Redirect extends Vue {
  @Prop({required: false})
  public route!: RawLocation

  public get portString() {
    if (window.location.port) {
      return ':80'
    }
    return ''
  }

  public created() {
    this.$router.replace(this.route)
  }
}
</script>
