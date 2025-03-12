<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-row v-if="color.x" no-gutters>
    <v-col v-if="controls" v-show="editing" cols="12" sm="7" md="4">
      <ac-patch-field
        density="compact"
        :patcher="color.patchers.note"
        hint="Label this color so others know what it's for. 'Hair', 'Eyes', or 'Hat' are all examples."
      />
    </v-col>
    <v-col v-show="!editing" cols="4">
      {{ color.x.note }}
    </v-col>
    <v-col
      v-if="controls"
      v-show="editing"
      cols="12"
      sm="4"
      md="2"
      offset-sm="1"
    >
      <ac-patch-field
        :patcher="color.patchers.color"
        :instant="true"
        density="compact"
      >
        <template #prepend>
          <ac-patch-field
            :instant="true"
            field-type="ac-color-prepend"
            :patcher="color.patchers.color"
          />
        </template>
      </ac-patch-field>
    </v-col>
    <v-col v-show="!editing" class="text-center color-notation" cols="5" md="4">
      {{ color.x.color }}
    </v-col>
    <v-col
      v-if="controls"
      v-show="editing"
      cols="10"
      md="3"
      lg="3"
      offset-md="1"
      align-self="center"
    >
      <div class="px-2 py-1" :style="modelStyle">&nbsp;</div>
    </v-col>
    <v-col v-show="!editing" cols="2" md="3" offset="1">
      <v-col class="px-2" :style="savedStyle"> &nbsp; </v-col>
    </v-col>
    <v-col
      v-if="editing"
      class="text-right text-lg-center d-flex flex-column justify-center"
      cols="2"
      md="1"
    >
      <ac-confirmation :action="color.delete">
        <template #confirmation-text>
          <span
            >Are you sure you wish to delete this color? This cannot be
            undone.</span
          >
        </template>
        <template #default="{ on }">
          <v-btn
            size="x-small"
            icon
            color="red"
            class="delete-button align-self-center"
            v-on="on"
          >
            <v-icon :icon="mdiDelete" />
          </v-btn>
        </template>
      </ac-confirmation>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { useSubject } from "@/mixins/subjective.ts"
import { SingleController } from "@/store/singles/controller.ts"
import { useEditable } from "@/mixins/editable.ts"
import { computed } from "vue"
import { mdiDelete } from "@mdi/js"
import { Color } from "@/store/characters/types/main"

const props = defineProps<{
  color: SingleController<Color>
  username: string
}>()

const { controls } = useSubject({ props })
const { editing } = useEditable(controls)

const width = "100%"
const modelStyle = computed(() => ({
  "background-color": props.color.patchers.color.model,
  width,
}))
const savedStyle = computed(() => ({
  "background-color": props.color.patchers.color.rawValue,
  width,
}))
</script>

<style>
.color-notation {
  font-family: monospace;
  text-transform: uppercase;
}
</style>
