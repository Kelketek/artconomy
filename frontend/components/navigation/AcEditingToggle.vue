<template>
  <v-speed-dial bottom right fixed v-model="editing" elevation-10 style="z-index: 4">
    <ac-speed-button
        slot="activator" nudge-top="2rem" nudge-right="1rem"
        :text="editing ? 'Lock' : 'Edit'"
    >
      <v-btn
             dark
             color="blue"
             fab
             hover
             large
             v-model="editing"
             class="edit-toggle"
      >
        <v-icon v-if="editing">lock</v-icon>
        <v-icon v-else>edit</v-icon>
      </v-btn>
    </ac-speed-button>
  </v-speed-dial>
</template>

<script lang="ts">
import Editable from '@/mixins/editable'
import Component, {mixins} from 'vue-class-component'
import AcSpeedButton from '@/components/wrappers/AcSpeedButton.vue'

  @Component({components: {AcSpeedButton}})
export default class AcEditingToggle extends mixins(Editable) {
    // Expect parent component to v-if switch this component if not appropriate.
    public controls = true
}
</script>
