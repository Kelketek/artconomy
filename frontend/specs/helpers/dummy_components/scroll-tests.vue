<template>
  <div>
    <div v-if="test === 'scrollableText'">
      <!--suppress XmlDuplicatedId -->
      <div id="form-example">
        <div class="scrollableText">
          <span class="error--text" id="scrollable-text-error"></span>
        </div>
      </div>
    </div>
    <div v-else-if="test === 'idOnly'">
      <!--suppress XmlDuplicatedId -->
      <div id="form-example">
        <span class="error--text" id="id-only-error"></span>
      </div>
    </div>
    <div v-else-if="test === 'noError'">
      <!--suppress XmlDuplicatedId -->
      <div id="form-example"></div>
    </div>
    <div v-else-if="test === 'noErrorNoId'">

    </div>
  </div>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'

@Component
class ErrorScrollTests extends Vue {
    @Prop()
    public test!: string
}
export default toNative(ErrorScrollTests)
</script>
