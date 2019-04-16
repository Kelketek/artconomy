<template>
  <v-flex>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        Try terms like:
        <p class="mb-0"><v-chip color="secondary" @click="search('refsheet')">refsheet</v-chip>
        <v-chip color="secondary" @click="search('badge')">badge</v-chip>
        <v-chip color="secondary" @click="search('stickers')">stickers</v-chip></p>
      </v-flex>
    </v-layout>
  </v-flex>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '@/components/views/search/mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
  @Component({
    components: {AcExpandedProperty, AcBoundField},
  })
export default class ProductHints extends mixins(SearchHints, Viewer) {
}
</script>
