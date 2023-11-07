<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Enter a name to search for.
      </v-col>
    </v-row>
  </v-col>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import SearchHints from '@/components/views/search/mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'

@Component({
  components: {
    AcExpandedProperty,
    AcBoundField,
  },
})
class ProfileExtra extends mixins(SearchHints, Viewer) {
}

export default toNative(ProfileExtra)
</script>
