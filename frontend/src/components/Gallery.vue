<template>
  <div class="container">
    <v-card>
      <v-layout>
        <v-flex v-if="user" class="mt-2">
          <ac-avatar :user="this.user" />
        </v-flex>
        <v-flex class="pt-2"><h1>{{title}}</h1></v-flex>
      </v-layout>
    </v-card>
    <ac-asset-gallery :endpoint="endpoint" :limit="35" />
  </div>
</template>

<script>
  import AcAssetGallery from './ac-asset-gallery'
  import AcAvatar from './ac-avatar'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'

  export default {
    props: ['username', 'title', 'endpoint'],
    mixins: [Perms, Viewer],
    components: {
      AcAvatar,
      AcAssetGallery},
    name: 'Gallery'
  }
</script>

<style scoped>

</style>