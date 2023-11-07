<template>
  <div></div>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Viewer from '../../mixins/viewer'

@Component({})
class RedirectToViewer extends mixins(Viewer) {
  @Prop({required: true})
  public viewName!: string

  public created() {
    if (!this.isLoggedIn) {
      this.$router.replace({
        name: 'Login',
        query: {next: this.$route.fullPath},
      })
      return
    }
    this.$router.push({
      name: this.viewName,
      params: {username: this.viewer!.username},
    })
  }
}

export default toNative(RedirectToViewer)
</script>
