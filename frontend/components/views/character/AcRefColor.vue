<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-row no-gutters v-if="color.x">
    <v-col cols="12" sm="7" md="4" v-if="controls" v-show="editing">
      <ac-patch-field density="compact" :patcher="color.patchers.note" hint="Label this color so others know what it's for. 'Hair', 'Eyes', or 'Hat' are all examples."/>
    </v-col>
    <v-col cols="4" v-show="!editing">{{color.x.note}}</v-col>
    <v-col cols="12" sm="4" md="2" offset-sm="1" v-if="controls" v-show="editing">
      <ac-patch-field :patcher="patchers.color" density="compact">
        <template v-slot:prepend>
          <ac-color-prepend v-model="patchers.color.model"/>
        </template>
      </ac-patch-field>
    </v-col>
    <v-col class="text-center color-notation" cols="5" md="4" v-show="!editing">{{color.x.color}}</v-col>
    <v-col cols="10" md="3" lg="3" offset-md="1" v-if="controls" v-show="editing" align-self="center">
      <div class="px-2 py-1" :style="modelStyle">
        &nbsp;
      </div>
    </v-col>
    <v-col cols="2" md="3" offset="1" v-show="!editing">
      <v-col class="px-2" :style="savedStyle">&nbsp;</v-col>
    </v-col>
    <v-col class="text-right text-lg-center d-flex flex-column justify-center" cols="2" md="1" v-if="editing">
      <ac-confirmation :action="color.delete">
        <template v-slot:confirmation-text>
          <span>Are you sure you wish to delete this color? This cannot be undone.</span>
        </template>
        <template v-slot:default="{on}">
          <v-btn size="x-small" icon v-on="on" color="red" class="delete-button align-self-center">
            <v-icon :icon="mdiDelete"/>
          </v-btn>
        </template>
      </ac-confirmation>
    </v-col>
  </v-row>
</template>

<style>
.color-notation {
  font-family: monospace;
  text-transform: uppercase;
}
</style>

<script setup lang="ts">
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'
import {useSubject} from '@/mixins/subjective.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {useEditable} from '@/mixins/editable.ts'
import {computed} from 'vue'
import {mdiDelete} from '@mdi/js'
import {Color} from '@/store/characters/types/main'

const props = defineProps<{color: SingleController<Color>, username: string}>()

const {controls} = useSubject({ props })
const {editing} = useEditable(controls)

const patchers = props.color.patchers
const width = '100%'
const modelStyle = computed(() => ({'background-color': patchers.color.model, width}))
const savedStyle = computed(() => ({'background-color': patchers.color.rawValue, width}))
</script>
