<template>
  <div></div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
import {Prop} from 'vue-property-decorator'

@Component
export default class RedirectToViewer extends mixins(Viewer) {
  @Prop({required: true})
  public viewName!: string

  public created() {
    if (!this.isLoggedIn) {
      this.$router.replace({name: 'Login', query: {next: this.$route.fullPath}})
      return
    }
    this.$router.push({name: this.viewName, params: {username: this.viewer!.username}})
  }
}
</script>
