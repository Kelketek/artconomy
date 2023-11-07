<template>
  <v-container>
    <v-row no-gutters>
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
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import {RouteLocationRaw} from 'vue-router'

@Component
class Redirect extends Vue {
  @Prop({required: false})
  public route!: RouteLocationRaw

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

export default toNative(Redirect)
</script>
