<template>
  <v-flex>
    <v-layout row wrap>
      <v-flex xs12 text-xs-center>
        Enter a name to search for.
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
export default class ProfileExtra extends mixins(SearchHints, Viewer) {
}
</script>
